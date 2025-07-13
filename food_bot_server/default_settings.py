import os

CHANNEL_SECRET = os.environ.get("CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")

GOOGLE_MAP_API_KEY = os.environ.get("GOOGLE_MAP_API_KEY")
GOOGLE_MAP_API_USAGE_FILE = os.environ.get("GOOGLE_MAP_API_USAGE_FILE", "api_usage.json")
GOOGLE_MAP_API_DAILY_QUOTA = int(os.environ.get("GOOGLE_MAP_API_DAILY_QUOTA", 30))  # 根據你的 Google Maps 免費額度調整
