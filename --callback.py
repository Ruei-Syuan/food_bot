
# ============================================================================================
# # 簡單判斷式
# @app.route("/callback2", methods=['POST'])
# def callback2():
#     # 獲取 LINE 送來的請求
#     signature = request.headers['X-Line-Signature']
#     body = request.get_data(as_text=True)

#     try:
#         handler.handle(body, signature)
#     except InvalidSignatureError:
#         abort(400)

#     return 'OK'

# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     user_message = event.message.text
#     keyword = [
#         'serena', 'celine', 'yunung'
#     ]
#     keyword2 = [
#         'sandy'
#     ]
#     # 根據使用者輸入的內容進行判斷
#     if user_message.lower() in keyword:
#         reply_message = "是組員"
#     elif user_message.lower() in keyword2:
#         reply_message = "是組長"
#     else:
#         reply_message = user_message

#     line_bot_api.reply_message(
#         event.reply_token,
#         TextSendMessage(text=reply_message)
#     )
# =============================

# ========================================================================
# 回傳一樣的訊息 (SDK example)
# https://pypi.org/project/line-bot-sdk/
# @app.route("/callback", methods=['POST'])
# def callback():
#     # get X-Line-Signature header value
#     signature = request.headers['X-Line-Signature']

#     # get request body as text
#     body = request.get_data(as_text=True)
#     app.logger.info("Request body: " + body)

#     # handle webhook body
#     try:
#         handler.handle(body, signature)
#     except InvalidSignatureError:
#         app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
#         abort(400)

#     return 'OK'

# @handler.add(MessageEvent, message=TextMessageContent)
# def handle_message(event):
#     with ApiClient(configuration) as api_client:
#         line_bot_api = MessagingApi(api_client)
#         line_bot_api.reply_message_with_http_info(
#             ReplyMessageRequest(
#                 reply_token=event.reply_token,
#                 messages=[TextMessage(text=event.message.text)]
#             )
#         )