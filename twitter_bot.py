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
    {"user": "jacksonhinkle", "url": "https://rss.app/feeds/v1.1/nQRfNkiu3xqp5UPX.json"},
    {"user": "Khamenei_fa", "url": "https://rss.app/feeds/v1.1/cxDtmcWC56oBdtTe.json"},
]

def send_to_bale(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Missing Bale Credentials")
        return False

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }

    try:
        res = requests.post(BALE_URL, json=payload, timeout=15)
        res.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Failed to send to Bale: {e}")
        return False

def load_sent_posts(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []
    return []

def save_sent_posts(file_path, posts):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(posts[-100:], f, ensure_ascii=False, indent=2)

def main():
    tehran = pytz.timezone("Asia/Tehran")
    now_str = datetime.now(tehran).strftime("%H:%M")

    sent_file = "sent.json"
    sent_posts = load_sent_posts(sent_file)
    new_found = False

    for feed in RSS_FEEDS:
        try:
            print(f"📡 Checking {feed['user']}...")
            response = requests.get(feed["url"], timeout=20)
            response.raise_for_status()

            if feed["url"].endswith(".json"):
                items = response.json().get("items", [])[:5]
                for item in items:
                    post_id = str(item.get("id") or item.get("url"))
                    title = item.get("title", "No title")
                    link = item.get("url", "")

                    if post_id not in sent_posts:
                        msg = f"📣 *{feed['user']}*\n\n{title}\n\n🔗 [Link]({link})\n⏰ {now_str}"
                        if send_to_bale(msg):
                            sent_posts.append(post_id)
                            new_found = True
            else:
                root = ET.fromstring(response.content)
                for item in root.findall("./channel/item")[:5]:
                    title_el = item.find("title")
                    link_el = item.find("link")

                    title = title_el.text if title_el is not None else "No title"
                    link = link_el.text if link_el is not None else ""
                    post_id = link

                    if post_id not in sent_posts:
                        msg = f"📣 *{feed['user']}*\n\n{title}\n\n🔗 [Link]({link})\n⏰ {now_str}"
                        if send_to_bale(msg):
                            sent_posts.append(post_id)
                            new_found = True

        except Exception as e:
            print(f"⚠️ Error checking {feed['user']}: {e}")

    if new_found:
        save_sent_posts(sent_file, sent_posts)
        print("✅ Database updated.")
    else:
        print("ℹ️ No new tweets found.")

if __name__ == "__main__":
    main()
