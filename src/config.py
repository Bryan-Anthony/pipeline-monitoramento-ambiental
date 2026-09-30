import os

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://api.thingspeak.com/channels/2412377/feeds.json?results=100&utm_source=chatgpt.com"
)

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "reports")

#API_USERNAME = os.getenv("")
#API_PASSWORD = os.getenv("")
