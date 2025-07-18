# ============================== ENVIROMENT ====================================
# OpenStreetMap + Overpass API 用的是這兩個免費的地圖
from flask import Flask, request #, abort

import os
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage,TextSendMessage, LocationSendMessage
import json
from linebot.v3.messaging import Configuration
# from API.location import save_to_db
from FUNC.search_btn import getNote, google_command, search, storeNote

app = Flask(__name__)

CHANNEL_SECRET = os.environ.get('CHANNEL_SECRET')
if not CHANNEL_SECRET:
    raise ValueError("❌ 環境變數 CHANNEL_SECRET 沒有設置，請在 Vercel 設定中確認")

CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN')
if not CHANNEL_ACCESS_TOKEN:
    raise ValueError("❌ 環境變數 CHANNEL_ACCESS_TOKEN 沒有設置，請在 Vercel 設定中確認")

# ==================================== FUNCTION CODE ===========================================
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

# ==============================================================================================
# 根目錄
@app.route("/")
def home():
    return "<h1>hello world</h1>"

# ==============================================================================================
# 使用者狀態暫存（建議正式使用請改用資料庫或 Redis）
user_states = {}
@app.route("/linebot2", methods=['POST'])
def linebot2():
    try:
        body = request.get_data(as_text=True)
        json_data = json.loads(body)

        events = json_data.get('events', [])
        if not events:
            # print("❌ 沒有 events，忽略這次請求")
            return 'OK'
        
        event = events[0]
        user_id = event['source']['userId']
        tk = event['replyToken']

        # 取得訊息文字（message 或 postback）
        msg_type = event['type']
        msg = ""
        # 是msg
        if msg_type == "message":
            # print('msg')
            msg = event['message']['text']
        elif msg_type == "postback":
            # print('postback')
            msg = event['postback']['data']

        print(f"🟡 使用者輸入：{msg}")

        # 狀態邏輯
        state = user_states.get(user_id, {}).get('state')
        
        # --- 主功能：食客筆記 ---
        if msg == "時刻超讚推薦":
            # line_bot_api.reply_message(tk, TextSendMessage(text="此功能尚未開發,謝謝!"))
            line_bot_api.reply_message(tk, TextSendMessage(text="請輸入要去的地方："))
            user_states[user_id] = {'state': 'waiting_for_google_search'}
            
        elif msg == "時刻搜尋":
            # line_bot_api.reply_message(tk, TextSendMessage(text="此功能尚未開發,謝謝!"))
            line_bot_api.reply_message(tk, TextSendMessage(text="請輸入要去的地方："))
            user_states[user_id] = {'state': 'waiting_for_search'}

        elif msg == "時刻筆記":
            line_bot_api.reply_message(tk, TextSendMessage(text="請輸入要新增筆記的關鍵字："))
            user_states[user_id] = {'state': 'waiting_for_title'}

        elif msg == "時刻回想":
            line_bot_api.reply_message(tk, TextSendMessage(text="請輸入要回想的關鍵字："))
            user_states[user_id] = {'state': 'waiting_for_keyword'}
        
        # subfunction 1
        elif state == "waiting_for_google_search":
            google_command(line_bot_api,tk,msg)
            user_states.pop(user_id)

        # subfunction 2
        elif state == "waiting_for_search":
            search(line_bot_api,tk,msg)
            user_states.pop(user_id)

        # subfunction 3
        elif state == "waiting_for_keyword":
            getNote(line_bot_api,tk,msg)
            user_states.pop(user_id)

        # subfunction 4        
        elif state == "waiting_for_title":
            user_states[user_id] = {'state': 'waiting_for_note'
                                    , 'title': msg
                                    }
            line_bot_api.reply_message(tk, TextSendMessage(text="請輸入餐廳名稱："))

        elif state == "waiting_for_note":
            storeNote(line_bot_api,tk,msg,user_states[user_id]['title'])
            user_states.pop(user_id)

        # others 
        else:
            line_bot_api.reply_message(tk, TextSendMessage(text="請點選下方【食客助手】"))
        # other answer
        
        
    except Exception as e:
        print('error:', e)
        
    return 'OK'

# =========================== MAIN CODE =======================================
# Vercel 自己會處理函式呼叫，不需要你手動啟動伺服器。
if __name__ == "__main__":
    app.run()