# from functools import _make_key
import requests
from linebot.models import TextSendMessage,TextSendMessage, LocationSendMessage
from API.location import get_location, save_to_db

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

    # else:
        # line_bot_api.reply_message(tk, TextSendMessage(text=f"❌ 找不到「{place_key}」的地點😢"))
        
def getNote(line_bot_api, tk,place_key):
    location_data = get_location(place_key)

    if not location_data:
        # 沒有查到資料
        line_bot_api.reply_message(tk, TextSendMessage(text=f"❌ 找不到「{place_key}」的地點😢"))
        return

    # 如果是單筆資料（dict）
    if isinstance(location_data, dict):
        location_message = LocationSendMessage(
            title=location_data['title'],
            address=location_data['address'],
            latitude=location_data['latitude'],
            longitude=location_data['longitude']
        )
        line_bot_api.reply_message(tk, location_message)

    # 如果是多筆資料（list）
    elif isinstance(location_data, list):
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

    # location_data = get_location(place_key)
    # if location_data:
    #     location_message = LocationSendMessage(
    #         title=location_data['title'],
    #         address=location_data['address'],
    #         latitude=location_data['latitude'],
    #         longitude=location_data['longitude']
    #     )
    #     line_bot_api.reply_message(tk, location_message)
    # else:
    #     line_bot_api.reply_message(tk, TextSendMessage(text="❌ 找不到「{place_key}」的地點😢"))
        
def searchNote(line_bot_api, tk, place, key):
    nominatim_url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': place,
        'format': 'json'
    }
    res = requests.get(nominatim_url, params=params, headers={"User-Agent": "my-linebot/1.0"})
    data = res.json()

    print(f"🟡 data：{data}")
    if data:
        data_content = data[0]
        lat = float(data_content['lat'])
        lon = float(data_content['lon'])
        address = data_content.get('display_name', place)

        print(place, address, lat, lon, key)
        save_to_db(place, address, lat, lon, key)
        line_bot_api.reply_message(tk, TextSendMessage(text=f"✅ 已存入「{place}」的相關資訊：{address}, {lat}, {lon}, {key}"))

    else:
        line_bot_api.reply_message(tk, TextSendMessage(text=f"❌ 找不到「{place}」的地點😢"))