from http import HTTPMethod
from flask import Flask, request

def create_app():
    app = Flask(__name__)
    app.config.from_object(f"{__name__}.default_settings")

    from . import linebot_api
    linebot_api.init_app(app)

    @app.route("/")
    def home():
        return "<h1>hello world</h1>"

    @app.route("/linebot-callback", methods=[HTTPMethod.POST])
    def linebot_callback():
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)
        app.linebot_handler.handle(body, signature)
        return "OK"

    @app.errorhandler(Exception)
    def general_exception(e: Exception):
        print(e)
        return "OK"

    return app
