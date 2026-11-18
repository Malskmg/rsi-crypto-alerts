import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SYMBOLS = [
    "AAVEUSDT",
    "HYPEUSDT",
]

TRIGGER_INTERVAL = "15m"
CONTEXT_INTERVAL = "4h"
RSI_PERIOD = 14

RSI_LOWER_LIMIT = 40
RSI_UPPER_LIMIT = 60

PARIS_TIMEZONE = "Europe/Paris"