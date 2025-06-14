import requests
from linebot.models import TextSendMessage,TextSendMessage, LocationSendMessage
from API.location import get_location
# from app import line_bot_api

def search(line_bot_api, tk,place_key):
    nominatim_url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': place_key,
        'format': 'json'
    }
    res = requests.get(nominatim_url, params=params, headers={"User-Agent": "my-linebot/1.0"})
    data = res.json()

    if data:
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

    else:
        line_bot_api.reply_message(tk, TextSendMessage(text=f"❌ 找不到「{place_key}」的地點😢"))
        
def getNote(line_bot_api, tk,place_key):
    location_data = get_location(place_key)
    if location_data:
        location_message = LocationSendMessage(
            title=location_data['title'],
            address=location_data['address'],
            latitude=location_data['latitude'],
            longitude=location_data['longitude']
        )
        line_bot_api.reply_message(tk, location_message)
    else:
        line_bot_api.reply_message(tk, TextSendMessage(text="❌ 找不到「{place_key}」的地點😢"))