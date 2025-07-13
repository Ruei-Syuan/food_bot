from functools import partial
from flask import Flask, current_app
from collections.abc import Callable

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.webhooks.models import UserSource
from linebot.v3.webhooks import (
    MessageEvent,
    PostbackEvent,
    TextMessageContent
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)

from FUNC.search_btn import getNote, google_command, search
from . import services

def ask_for_title(
    reply_token: str,
    message: str,
    user_id: str,
):
    current_app.linebot_db[user_id] = partial(services.store_note, keyword=message)
    current_app.linebot_reply_message(reply_token, "請輸入餐廳名稱：")
    return

MESSAGE_ACTION_MAPPING: dict[str, tuple[str, Callable]] = {
    "時刻超讚推薦": ("請輸入要去的地方", google_command),
    "時刻搜尋": ("請輸入要去的地方", search),
    "時刻筆記": ("請輸入要新增筆記的關鍵字：", ask_for_title),
    "時刻回想": ("請輸入要回想的關鍵字：", getNote),
}

def register_handlers(handler: WebhookHandler):
    @handler.add(MessageEvent, message=TextMessageContent)
    def handle_text_msg(event: MessageEvent):
        source: UserSource = event.source
        user_id = source.user_id
        message = event.message.text

        if (result := MESSAGE_ACTION_MAPPING.get(message)):
            reply_msg, action_func = result

            current_app.linebot_db[user_id] = action_func
            current_app.linebot_reply_message(event.reply_token, reply_msg)
            return

        if not (action_func := current_app.linebot_db.get(user_id)):
            current_app.linebot_reply_message(event.reply_token, reply_msg="請點選下方【食客助手】")
            return
        
        action_func(
            reply_token=event.reply_token,
            message=message,
            user_id=user_id,
        )
        return

    @handler.add(PostbackEvent)
    def handle_postback():
        pass


def init_app(app: Flask):
    config = Configuration(access_token=app.config["CHANNEL_ACCESS_TOKEN"])
    handler = WebhookHandler(channel_secret=app.config["CHANNEL_SECRET"])

    app.linebot_handler = handler
    app.line_api_client_maker = lambda: ApiClient(config)
    app.linebot_db = dict() # dict[str, Callable], str for user_id

    def _reply_text_message(reply_token: str, reply_msg: str):
        with current_app.line_api_client_maker() as api_client:
            MessagingApi(api_client).reply_message(
                ReplyMessageRequest(
                    replyToken=reply_token,
                    messages=[TextMessage(text=reply_msg)]
                )
            )
    app.linebot_reply_message = _reply_text_message

    return
