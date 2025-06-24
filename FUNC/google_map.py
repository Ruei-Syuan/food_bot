# from flask import Flask, request, abort
# from linebot import LineBotApi, WebhookHandler
import math
from linebot.models import MessageEvent, TextMessage, TextSendMessage, LocationMessage
from linebot.exceptions import InvalidSignatureError
import requests

# import requests
# import sqlite3
# import os
# from datetime import datetime, date

# ====== 設定 =======
# LINE_CHANNEL_ACCESS_TOKEN = "EjecQF8vpI0Kr2Zooc+eDaiPugzvpQR9LCn8iavtR0udSdajY0y0HkymNjQdBj1ysfiRPds344zX+QrHQ3GoROD2TVt28pR8yyAc+SS7pWVQ7gmB7X4UtLBa3cnn8xCPZ9+HymfJABtEjoDr4dJukAdB04t89/1O/w1cDnyilFU="
# LINE_CHANNEL_SECRET = "4d93921e936359c7fa23e607da118560"
GOOGLE_MAP_API_KEY = "AIzaSyCFN2Oz9qdBqecHZkRHDzSSUyi1eFWguqg"

# BASE_DIR = os.path.dirname(os.path.abspath(_file_))
# DB_PATH = os.path.join(BASE_DIR, "favorite_restaurants.db")
# USAGE_DB_PATH = os.path.join(BASE_DIR, "api_usage.db")

# ====== 工具方法 =======
# def calculate_distance(lat1, lon1, lat2, lon2):
#     R = 6371
#     lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
#     dlat = lat2 - lat1
#     dlon = lon2 - lon1
#     a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
#     c = 2 * math.asin(math.sqrt(a))
#     return R * c

def find_nearby_restaurants(keyword, latitude, longitude, radius=500):
    # if not check_api_limit():
    #     return "API 使用次數已達每日上限（50 次），請明天再試。"

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAP_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.id,places.location"
    }
    payload = {
        "includedTypes": ["restaurant"],
        "locationRestriction": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": float(radius)
            }
        },
        "maxResultCount": 10
    }
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    if "places" not in data:
        return []
    results = []
    for p in data["places"]:
        name = p.get("displayName", {}).get("text", "未知")
        address = p.get("formattedAddress", "未知地址")
        rating = p.get("rating", 0)
        count = p.get("userRatingCount", 0)
        pid = p.get("id")
        loc = p.get("location", {})
        if rating >= 4:
            results.append({
                "name": name, "address": address, "rating": rating,
                "user_ratings_total": count, "google_maps_link": f"https://www.google.com/maps/place/?q=place_id:{pid}",
                "latitude": loc.get("latitude"), "longitude": loc.get("longitude"),
                "place_id": pid
            })
    return results

# ====== Geocode 文字查座標 =======
# def geocode_text(query):
#     # if not check_api_limit():
#     #     return None, None

#     url = f"https://maps.googleapis.com/maps/api/geocode/json?address={query}&key={GOOGLE_MAP_API_KEY}"
#     resp = requests.get(url)
#     data = resp.json()
#     if data.get("results"):
#         location = data["results"][0]["geometry"]["location"]
#         return location["lat"], location["lng"]
#     return None, None


# @app.route("/callback", methods=["POST"])
# def callback():
#     signature = request.headers["X-Line-Signature"]
#     body = request.get_data(as_text=True)
#     try:
#         handler.handle(body, signature)
#     except InvalidSignatureError:
#         abort(400)
#     return "OK"

# @handler.add(MessageEvent, message=TextMessage)
# def handle_text(event):
    # text = event.message.text.strip()
    # if text == "查看收藏":
    #     reply = view_all_favorites()
    # elif text == "查看剩餘次數":
    #     left = get_remaining_api_calls()
    #     reply = f"今天剩餘的 API 使用次數為：{left} 次"
    # else:
    #     lat, lng = geocode_text(text)
    #     # if lat and lng:
    #         results = find_nearby_restaurants(text, lat, lng)
    #         # if isinstance(results, str):  # 被 API 限制了
    #         #     reply = results
    #         # elif results:
    #             reply = f"\ud83d\udd0d {text} 附近推薦餐廳：\n"
    #             for r in results[:5]:
    #                 reply += f"\n\ud83c\udf74 {r['name']}\n\u2b50 {r['rating']} | {r['address']}\n{r['google_maps_link']}\n"
    #         else:
    #             reply = f"找不到 {text} 附近的餐廳"
    #     else:
    #         reply = "無法辨識地點或 API 已達上限，請明天再試"
    # line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

# @handler.add(MessageEvent, message=LocationMessage)
# def handle_location(event):
#     lat = event.message.latitude
#     lng = event.message.longitude
#     results = find_nearby_restaurants("", lat, lng)
#     if isinstance(results, str):
#         reply = results
#     elif results:
#         reply = "\ud83d\udd0d 你附近推薦餐廳：\n"
#         for r in results[:5]:
#             reply += f"\n\ud83c\udf74 {r['name']}\n\u2b50 {r['rating']} | {r['address']}\n{r['google_maps_link']}\n"
#     else:
#         reply = "找不到你附近的餐廳"
#     line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
