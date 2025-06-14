# ============================== ENVIROMENT ====================================
from flask import Flask, abort, request #, abort

import os
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage,TextSendMessage, LocationSendMessage
# MessageEvent, TextMessage, 
import json
import sqlite3

app = Flask(__name__)

# CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
# CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')

CHANNEL_SECRET = os.environ.get('CHANNEL_SECRET')
if not CHANNEL_SECRET:
    raise ValueError("❌ 環境變數 CHANNEL_SECRET 沒有設置，請在 Vercel 設定中確認")

CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN')
if not CHANNEL_ACCESS_TOKEN:
    raise ValueError("❌ 環境變數 CHANNEL_ACCESS_TOKEN 沒有設置，請在 Vercel 設定中確認")
# ========================== FUNCTION CODE =========================================
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

# ==============================================================================================
# 根目錄
@app.route("/")
def home():
    return "<h1>hello world</h1>"

# ==============================================================================================
# 建立資料庫連線
def get_location(text):
    conn = sqlite3.connect('LINEBOT_DB.db')  # 連接資料庫
    cursor = conn.cursor()

    # 查詢符合輸入內容的地點
    cursor.execute("SELECT title, address, latitude, longitude FROM food_map WHERE keyword=?", (text,))
    row = cursor.fetchone()
    
    conn.close()  # 關閉連線

    if row:
        return {'title': row[0], 'address': row[1], 'latitude': row[2], 'longitude': row[3]}
    else:
        return False
    
@app.route("/callback2", methods=['POST'])
def callback2():
    print("Webhook received ✅")
    return 'OK', 200

@app.route("/linebot2", methods=['POST'])
def linebot2():
    try:
        body = request.get_data(as_text=True)
        json_data = json.loads(body)

        # signature = request.headers['X-Line-Signature']

        msg = json_data['events'][0]['message']['text']
        tk = json_data['events'][0]['replyToken']

        location_data = get_location(msg)

        if location_data:
            location_message = LocationSendMessage(
                title=location_data['title'],
                address=location_data['address'],
                latitude=location_data['latitude'],
                longitude=location_data['longitude']
            )
            line_bot_api.reply_message(tk, location_message)
        else:
            text_message = TextSendMessage(text='找不到相關地點')
            line_bot_api.reply_message(tk, text_message)

    except Exception as e:
        print('error:', e)
        return 'OK'

    return 'OK'

# =========================== MAIN CODE =======================================
# Vercel 自己會處理函式呼叫，不需要你手動啟動伺服器。
if __name__ == "__main__":
    app.run()