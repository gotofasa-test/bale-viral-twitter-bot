import os
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz

BOT_TOKEN = os.getenv("BALE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BALE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"

RSS_FEEDS = [
    {
        "user": "jacksonhinkle",
        "url": "https://rss.app/feeds/v1.1/nQRfNkiu3xqp5UPX.json"
    },
    {
        "user": "Khamenei_fa",
        "url": "https://rss.app/feeds/v1.1/cxDtmcWC56oBdtTe.json"
    }
]


def send_to_bale(text):

    if not BOT_TOKEN or not CHAT_ID:
        print("Missing Bale credentials")
        return False

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }

    try:
        res = requests.post(BALE_URL, json=payload, timeout=15)
        res.raise_for_status()
        print("✅ Message sent")
        return True

    except Exception as e:
        print("❌ Bale error:", e)
        return False


def load_sent_posts(file_path):

    if os.path.exists(file_path):

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)

        except:
            return []

    return []


def save_sent_posts(file_path, posts):

    posts
