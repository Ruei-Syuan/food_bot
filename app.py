# ============================== ENVIROMENT ====================================
from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
import os
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage,TextSendMessage, LocationSendMessage
import json
import sqlite3

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')

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

@app.route("/linebot2", methods=['POST'])
def linebot2():
    body = request.get_data(as_text=True)
    json_data = json.loads(body)
    print(json_data)

    try:
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)
        
        msg = json_data['events'][0]['message']['text']
        # print('tk: ',tk)
        print('msg: ',msg)
        
        location_data = get_location(msg)  # 從資料庫查詢地點
        # print('location_data: ',location_data)
        
        if location_data:
            location_message = LocationSendMessage(
                title=location_data['title'],
                address=location_data['address'],
                latitude=location_data['latitude'],
                longitude=location_data['longitude']
            )
            tk = json_data['events'][0]['replyToken']
            # print('tk: ',tk)
            print(location_message)
            line_bot_api.reply_message(tk, location_message)
        else:
            text_message = TextSendMessage(text='找不到相關地點')
            tk = json_data['events'][0]['replyToken']
            # print('tk: ',tk)
            line_bot_api.reply_message(tk, text_message)
    except:
        print('error')

    return 'OK'
# =========================== MAIN CODE =======================================
if __name__ == "__main__":
    app.run()
