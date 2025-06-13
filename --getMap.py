# import requests
# import json
# from flask import Flask, request

# app = Flask(__name__)

# # LINE Channel Access Token
# LINE_ACCESS_TOKEN = "YOUR_LINE_ACCESS_TOKEN"

# # Google Places API Key
# GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"

# def search_nearby_restaurants(latitude, longitude):
#     url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
#     params = {
#         "location": f"{latitude},{longitude}",
#         "radius": 2000,  # 2 公里範圍內
#         "type": "restaurant",
#         "key": GOOGLE_API_KEY
#     }
#     response = requests.get(url, params=params)
#     places = response.json().get("results", [])
    
#     message = "附近的美食：\n"
#     for place in places[:5]:  # 取前 5 個
#         message += f"{place['name']} - ⭐ {place.get('rating', 'N/A')}\n"
    
#     return message

# def reply_message(reply_token, text):
#     url = "https://api.line.me/v2/bot/message/reply"
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
#     }
#     data = {
#         "replyToken": reply_token,
#         "messages": [{"type": "text", "text": text}]
#     }
#     requests.post(url, headers=headers, json=data)

# @app.route("/webhook", methods=["POST"])
# def webhook():
#     body = request.json
#     event = body["events"][0]

#     if event["type"] == "message" and event["message"]["type"] == "location":
#         latitude = event["message"]["latitude"]
#         longitude = event["message"]["longitude"]
#         reply_token = event["replyToken"]
        
#         # 呼叫 Google Maps API 搜尋附近美食
#         food_message = search_nearby_restaurants(latitude, longitude)
#         reply_message(reply_token, food_message)

#     return "OK"

# if __name__ == "__main__":
#     app.run(port=5000)