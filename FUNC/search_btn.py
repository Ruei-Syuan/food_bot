import datetime
import json
import os
import requests
from linebot.models import TextSendMessage,TextSendMessage, LocationSendMessage
from API.location import create_table, save_to_db, get_location
from linebot.models import FlexSendMessage # 滑動選單

GOOGLE_MAP_API_KEY = os.getenv("GOOGLE_MAP_API_KEY")
DEFAULT_IMAGE_URL = "https://fakeimg.pl/640x400/4B2E2E/ffffff/?text=No+Street+View"

API_USAGE_FILE = "api_usage.json"
DAILY_API_LIMIT = 2  # 根據你的 Google Maps 免費額度調整

# 檢核 google api 使用次數
def check_and_increment_api_usage():
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(API_USAGE_FILE):
        with open(API_USAGE_FILE, "r") as f:
            usage_data = json.load(f)
    else:
        usage_data = {}

    today_count = usage_data.get(today, 0)
    if today_count >= DAILY_API_LIMIT:
        return False  # 超過限制

    usage_data[today] = today_count + 1

    with open(API_USAGE_FILE, "w") as f:
        json.dump(usage_data, f)

    return True

# 關鍵字查經緯度
def geocode_text(query):
    # if not check_api_limit():
    #     return None, None

    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={query}&key={GOOGLE_MAP_API_KEY}"
    resp = requests.get(url)
    data = resp.json()
    if data.get("results"):
        location = data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    
    return None, None

def get_street_view_image_url(latitude, longitude):
    metadata_url = (
        f"https://maps.googleapis.com/maps/api/streetview/metadata"
        f"?location={latitude},{longitude}"
        f"&key={GOOGLE_MAP_API_KEY}"
    )
    
    try:
        response = requests.get(metadata_url)
        data = response.json()
        if data.get("status") == "OK":
            # 有街景就回傳街景圖片 URL
            return (
                f"https://maps.googleapis.com/maps/api/streetview"
                f"?size=640x400"
                f"&location={latitude},{longitude}"
                f"&fov=80&heading=0&pitch=0"
                f"&key={GOOGLE_MAP_API_KEY}"
            )
        else:
            # 沒有街景則回傳預設圖片
            return DEFAULT_IMAGE_URL
    except Exception as e:
        # print(f"Street View 檢查失敗: {e}")
        return DEFAULT_IMAGE_URL
    
def google_command(line_bot_api, tk, place_key, radius=500):
    if not check_and_increment_api_usage():
        line_bot_api.reply_message(
            tk,
            TextSendMessage(text="Google Map 搜尋已抵達當日上限次數，請明天再試 🥲")
        )
        return
    
    if not isinstance(GOOGLE_MAP_API_KEY, str) or not GOOGLE_MAP_API_KEY:
        raise ValueError("GOOGLE_MAP_API_KEY 未正確設置")

    latitude, longitude = geocode_text(place_key)

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAP_API_KEY,
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
                "radius": float(radius)
            }
        },
        "maxResultCount": 5 #卡5筆
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        # print(f"[API ERROR] {e}")
        line_bot_api.reply_message(tk, TextSendMessage(text="Google 地圖服務發生錯誤，請稍後再試。"))
        return

    if "places" not in data:
        line_bot_api.reply_message(tk, TextSendMessage(text=f"找不到「{place_key}」附近的餐廳資訊。"))
        return

    results = []
    for place in data["places"]:
        rating = place.get("rating", 0)
        if rating <= 4: #大於4星等才回傳
            continue
        
        # print(place)
        results.append({
            "name": place.get("displayName", {}).get("text", "未知"),
            "address": place.get("formattedAddress", "未知地址"),
            "rating": rating,
            "latitude": place.get("location", {}).get("latitude", "未知緯度"),
            "longitude": place.get("location", {}).get("longitude", "未知經度"),
            "user_ratings_total": place.get("userRatingCount", 0),
            "google_maps_link": f"https://www.google.com/maps/place/?q=place_id:{place.get('id')}"
        })

    if not results:
        line_bot_api.reply_message(tk, TextSendMessage(text=f"找不到「{place_key}」附近評價高的餐廳😢"))
        return

    # 建立 Flex Message bubbles
    bubbles = []
    for r in results[:5]:  # 最多 5 個 bubble
        bubble = {
            "type": "bubble",
            "size": "kilo",
            "hero": {
                "type": "image",
                "url": get_street_view_image_url(r['latitude'], r['longitude']), #改成街景圖
                # "https://maps.gstatic.com/tactile/pane/default_geocode-2x.png",  # 預設餐廳圖
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": r['name'],
                        "weight": "bold",
                        "size": "lg",
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": f"⭐ {r['rating']}  |  {r['user_ratings_total']} 評價",
                        "size": "sm",
                        "color": "#999999",
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": r['address'],
                        "wrap": True,
                        "size": "sm",
                        "margin": "md"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": "在 Google Maps 查看",
                            "uri": r['google_maps_link']
                        }
                    }
                ],
                "flex": 0
            }
        }
        bubbles.append(bubble)

    flex_message = FlexSendMessage(
        alt_text=f"「{place_key}」附近的美食推薦",
        contents={
            "type": "carousel",
            "contents": bubbles
        }
    )
    line_bot_api.reply_message(tk, flex_message)

def search(line_bot_api, tk,place_key):
    nominatim_url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': place_key,
        'format': 'json'
    }
    res = requests.get(nominatim_url, params=params, headers={"User-Agent": "my-linebot/1.0"})
    data = res.json()

    if not data:  # early return
        line_bot_api.reply_message(tk, TextSendMessage(text=f"❌ 找不到「{place_key}」的地點😢"))
        return 'OK'
    
    # if data:
    place = data[0]
    lat = float(place['lat'])
    lon = float(place['lon'])
    address = place.get('display_name', place_key)

    # 查詢附近餐廳 using Overpass API
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
    node["amenity"="restaurant"](around:300,{lat},{lon});
    way["amenity"="restaurant"](around:300,{lat},{lon});
    relation["amenity"="restaurant"](around:300,{lat},{lon});
    );
    out center;
    """
    overpass_res = requests.post(overpass_url, data={'data': overpass_query})
    overpass_data = overpass_res.json()

    restaurant_names = []
    if 'elements' in overpass_data:
        for el in overpass_data['elements']:
            name = el.get('tags', {}).get('name')
            if name and name not in restaurant_names:
                restaurant_names.append("🍽️ " + name)

    # 建立訊息清單
    reply_messages = [
        LocationSendMessage(
            title=place_key,
            address=address,
            latitude=lat,
            longitude=lon
        )
    ]

    if restaurant_names:
        reply_messages.append(TextSendMessage(text=f"「{place_key}」附近的美食推薦：\n" + "\n".join(restaurant_names[:5])))
    else:
        reply_messages.append(TextSendMessage(text=f"「{place_key}」附近找不到具名餐廳😢"))

    line_bot_api.reply_message(tk, reply_messages)
        
def getNote(line_bot_api, tk,place_key):
    location_data = get_location(place_key)

    if not location_data:
        # 沒有查到資料
        line_bot_api.reply_message(tk, TextSendMessage(text=f"❌ 找不到「{place_key}」的地點😢"))
        return

    # 如果是單筆資料（dict）
    if isinstance(location_data, dict):
        # print(f"🟡 是單筆資料")
        location_message = LocationSendMessage(
            title=location_data['title'],
            address=location_data['address'],
            latitude=location_data['latitude'],
            longitude=location_data['longitude']
        )
        line_bot_api.reply_message(tk, location_message)

    # 如果是多筆資料（list）
    elif isinstance(location_data, list):
        # print(f"🟡 是多筆資料")
        location_messages = []
        for item in location_data[:5]:  # 最多回傳 5 筆，LINE 限制
            location_messages.append(
                LocationSendMessage(
                    title=item['title'],
                    address=item['address'],
                    latitude=item['latitude'],
                    longitude=item['longitude']
                )
            )
        line_bot_api.reply_message(tk, location_messages)
        
def storeNote(line_bot_api, tk, place, key):
    # 建表（只需執行一次）
    create_table()

    nominatim_url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': place,
        'format': 'json'
    }
    res = requests.get(nominatim_url, params=params, headers={"User-Agent": "my-linebot/1.0"})
    data = res.json()

    # print(f"🟡 data：{data}")
    if data:
        data_content = data[0]
        lat = float(data_content['lat'])
        lon = float(data_content['lon'])
        address = data_content.get('display_name', place)

        # print(f"🟡 data：{place}, {address}, {lat}, {lon}, {key}")
        save_to_db(place, address, lat, lon, key)
        line_bot_api.reply_message(tk, TextSendMessage(text=f"✅ 已存入「{place}」的相關資訊：{address}, {lat}, {lon}, {key}"))

    else:
        line_bot_api.reply_message(tk, TextSendMessage(text=f"❌ 找不到「{place}」的地點😢"))