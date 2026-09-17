import os 

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://api.thingspeak.com/channels/2412377/feeds.json?results=2&utm_source=chatgpt.com"
)

#API_USERNAME = os.getenv("")
#API_PASSWORD = os.getenv("")
