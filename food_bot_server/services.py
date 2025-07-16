from datetime import datetime
import json
import os

from flask import current_app as app
import requests

from . import db
from linebot.v3.messaging import LocationMessage, TextMessage, FlexMessage

__all__ = (
    'store_note',
    'get_note',
    'search_location_neighborhood',
    'google_map_search',
)

def store_note(
    reply_token,
    message: str,
    *,
    keyword: str,
    **kwargs,
) -> None:
    """
    Store place information in note

    Args:
        reply_token
        message (str): place name from user input
        **kwargs,
    """
    location = message

    nominatim_url = "https://nominatim.openstreetmap.org/search"
    params = dict(
        q=message,
        format='json',
    )

    try:
        resp = requests.get(nominatim_url, params=params, headers={"User-Agent": "my-linebot/1.0"})
        resp.raise_for_status()
        json_data = resp.json()
    except Exception as e:
        # TODO: try-catch for unexpected result?
        print(e)
        pass

    if not json_data:
        app.linebot_reply_message(
            reply_token,
            reply_msg=f"❌ 找不到「{location}」的地點😢",
        )
        return
    
    db.store_record(
        title=location,
        latitude=(latitude := float(json_data[0]['lat'])),
        longitude=(longitude := float(json_data[0]['lon'])),
        address=(address := json_data[0].get('display_name', message)),
        keyword=keyword,
    )

    app.linebot_reply_message(
        reply_token,
        reply_msg=f"✅ 已存入「{location}」的相關資訊：{address}, {latitude}, {longitude}, {keyword}",
    )

    return


def get_note(
    reply_token,
    message: str,
    **kwargs,
):
    location = message

    if not (location_data := db.query_record(text=location)):
        app.linebot_reply_message(
            reply_token,
            reply_msg=f"❌ 找不到「{location}」的地點😢",
        )
    
    locations_data_list = [location_data] if isinstance(location_data, dict) else location_data
    location_messages = list(map(
        lambda item: LocationMessage(
            title=item['title'],
            address=item['address'],
            latitude=item['latitude'],
            longitude=item['longitude']
        ),
        locations_data_list[:5],
        # LINE only accept 5 messages at most
        # ref: linebot/v3/messaging/models/reply_message_request.py
    ))

    app.linebot_reply_message(
        reply_token,
        reply_msg=location_messages,
    )
    return


def search_location_neighborhood(
    reply_token,
    message: str,
    **kwargs,
):
    location = message

    nominatim_url = "https://nominatim.openstreetmap.org/search"
    params = dict(
        q=location,
        format='json',
    )

    try:
        resp = requests.get(nominatim_url, params=params, headers={"User-Agent": "my-linebot/1.0"})
        resp.raise_for_status()
        json_data = resp.json()
    except Exception as e:
        print(e)
        # TODO: try-catch for unexpected result?
        pass

    if not json_data:
        app.linebot_reply_message(
            reply_token,
            reply_msg=f"❌ 找不到「{location}」的地點😢",
        )
        return
    
    location_data = json_data[0]

    location_message = LocationMessage(
        title=location,
        address=location_data.get('display_name', location),
        latitude=(latitude := float(location_data['lat'])),
        longitude=(longitude := float(location_data['lon'])),
    )
    
    # Overpass API
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = (
        '[out:json];'
        '('
        'node["amenity"="restaurant"](around:300,{latitude},{longitude});'
        'way["amenity"="restaurant"](around:300,{latitude},{longitude});'
        'relation["amenity"="restaurant"](around:300,{latitude},{longitude});'
        ');'
        'out center;'
    ).format(latitude=latitude, longitude=longitude)

    try:
        overpass_resp = requests.post(overpass_url, data={'data': overpass_query})
        overpass_resp.raise_for_status()
        overpass_data = overpass_resp.json()
    except Exception as e:
        print(e)
        # TODO: try-catch for unexpected result?
        pass

    restaurant_names = map(
        lambda item: item.get('tags', dict()).get('name'),
        overpass_data.get("elements", list()),
    )
    # remove empty item
    restaurant_names = filter(
        None,
        restaurant_names,
    )
    restaurant_names = list(map(
        lambda item: f"🍽️  {item}",
        restaurant_names,
    ))

    if not restaurant_names:
        app.linebot_reply_message(
            reply_token,
            reply_msg=[
                location_message,
                TextMessage(f"「{location}」附近找不到具名餐廳😢"),
            ],
        )
        return
    
    app.linebot_reply_message(
        reply_token,
        reply_msg=[
            location_message,
            # NOTE: no need to limit restaurant_names name here
            TextMessage(f"「{location}」附近的美食推薦：\n{'\n'.join(restaurant_names)}")
        ],
    )
    return


def check_and_increment_api_usage():
    """檢核 google api 使用次數"""
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists((usage_file := app.config["GOOGLE_MAP_API_USAGE_FILE"])):
        with open(usage_file, "r") as f:
            usage_data = json.load(f)
    else:
        usage_data = {}

    today_count = usage_data.get(today, 0)
    if today_count >= app.config["GOOGLE_MAP_API_DAILY_QUOTA"]:
        return False  # 超過限制

    usage_data[today] = today_count + 1

    with open(usage_file, "w") as f:
        json.dump(usage_data, f)

    return True



def geocode_text(query):
    """關鍵字查經緯度"""
    # if not check_api_limit():
    #     return None, None
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={query}&key={app.config["GOOGLE_MAP_API_KEY"]}"
    resp = requests.get(url)
    data = resp.json()
    if data.get("results"):
        location = data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    
    return None, None


def get_street_view_image_url(latitude, longitude):
    DEFAULT_IMAGE_URL = "https://fakeimg.pl/640x400/4B2E2E/ffffff/?text=No+Street+View"

    metadata_url = (
        f"https://maps.googleapis.com/maps/api/streetview/metadata"
        f"?location={latitude},{longitude}"
        f"&key={app.config["GOOGLE_MAP_API_KEY"]}"
    )
    
    try:
        resp = requests.get(metadata_url)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        # print(f"Street View 檢查失敗: {e}")
        return DEFAULT_IMAGE_URL
    
    if data.get("status") != "OK":
            # 沒有街景則回傳預設圖片
            return DEFAULT_IMAGE_URL

    # 有街景就回傳街景圖片 URL
    return (
        f"https://maps.googleapis.com/maps/api/streetview"
        f"?size=640x400"
        f"&location={latitude},{longitude}"
        f"&fov=80&heading=0&pitch=0"
        f"&key={app.config["GOOGLE_MAP_API_KEY"]}"
    )

def google_map_search_by_geo_metrics(
    latitude,
    longitude,
    radius,
):
    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": app.config["GOOGLE_MAP_API_KEY"],
        "X-Goog-FieldMask": (
            "places.displayName,"
            "places.formattedAddress,"
            "places.rating,"
            "places.userRatingCount,"
            "places.id,"
            "places.location"
        )
    }
    payload = {
        "includedTypes": ["restaurant"],
        "locationRestriction": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": float(radius),
            },
        },
        "maxResultCount": 5, #卡5筆
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        # print(f"[API ERROR] {e}")
        return
    

def google_map_search(
    reply_token,
    message: str,
    radius=500,
    **kwargs
):
    location = message

    if not check_and_increment_api_usage():
        app.linebot_reply_message(
            reply_token,
            reply_msg="Google Map 搜尋已抵達當日上限次數，請明天再試 🥲",
        )
        return

    latitude, longitude = geocode_text(location)
    google_map_data = google_map_search_by_geo_metrics(
        latitude=latitude,
        longitude=longitude,
        radius=radius,
    )

    if not google_map_data:
        app.linebot_reply_message(
            reply_token,
            reply_msg="Google 地圖服務發生錯誤，請稍後再試。",
        )
        return

    if "places" not in google_map_data:
        app.linebot_reply_message(
            reply_token,
            reply_msg=f"找不到「{location}」附近的餐廳資訊。",
        )
        return
    
    places = filter(
        # only pick places rated over 4 stars
        lambda place: place.get("rating", 0) >= 4,
        google_map_data["places"],
    )
    places = map(
        lambda place: dict(
            name               = place.get("displayName", dict()).get("text", "未知"),
            address            = place.get("formattedAddress", "未知地址"),
            rating             = place["rating"],
            latitude           = place.get("location", {}).get("latitude", "未知緯度"),
            longitude          = place.get("location", {}).get("longitude", "未知經度"),
            user_ratings_total = place.get("userRatingCount", 0),
            google_maps_link   = f"https://www.google.com/maps/place/?q=place_id:{place.get('id')}",
        ),
        places,
    )
    places = list(places)[:5]

    if not places:
        app.linebot_reply_message(
            reply_token,
            reply_msg=f"找不到「{location}」附近評價高的餐廳😢",
        )
        return
    
    def _yield_bubble(place):
        yield "type", "bubble"
        yield "size", "kilo"
        yield "hero", {
            "type": "image",
            "url": get_street_view_image_url(place['latitude'], place['longitude']), #改成街景圖
            # "https://maps.gstatic.com/tactile/pane/default_geocode-2x.png",  # 預設餐廳圖
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover"
        }
        def _yield_body_contents():
            yield dict(
                type="text",
                text=place["name"],
                weight="bold",
                size="lg",
                wrap=True,
            )
            yield dict(
                type="text",
                text=f"⭐ {place['rating']}  |  {place['user_ratings_total']} 評價",
                size="sm",
                color="#999999",
                margin="md",
            )
            yield dict(
                type   = "text",
                text   = place['address'],
                wrap   = True,
                size   = "sm",
                margin = "md"
            )
        yield "body", {
            "type": "box",
            "layout": "vertical",
            "contents": list(_yield_body_contents()),
        }
        yield "footer", {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [{
                "type": "button",
                "style": "link",
                "height": "sm",
                "action": {
                    "type": "uri",
                    "label": "在 Google Maps 查看",
                    "uri": place['google_maps_link']
                },
            }],
            "flex": 0
        }
        
    message = FlexMessage(
        altText=f"「{location}」附近的美食推薦",
        contents={
            "type": "carousel",
            "contents": list(map(
                lambda place: dict(_yield_bubble(place)),
                places,
            ))
        }
    )
    app.linebot_reply_message(
        reply_token,
        reply_msg=message,
    )
    return
