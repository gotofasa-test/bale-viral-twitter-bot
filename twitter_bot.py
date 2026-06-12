import os
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz

# تنظیمات محیطی
BOT_TOKEN = os.getenv("BALE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
BALE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"

# لیست فیدهای هدف (می‌توانی لینک‌های RSS.app خودت را اینجا بگذاری)
RSS_FEEDS = [
    
    {"user": "jacksonhinkle", "url": "https://rss.app/feeds/v1.1/nQRfNkiu3xqp5UPX.json"},
    {"user": "Khamenei_fa", "url": "https://rss.app/feeds/v1.1/cxDtmcWC56oBdtTe.json"}
]

def send_to_bale(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Missing Bale Credentials")
        return
    
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        res = requests.post(BALE_URL, json=payload, timeout=15)
        res.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to send to Bale: {e}")

def load_sent_posts(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def main():
    tehran = pytz.timezone("Asia/Tehran")
    now_str = datetime.now(tehran).strftime("%H:%M")
    sent_file = "sent.json"
    
    sent_posts = load_sent_posts(sent_file)
    new_found = False

    for feed in RSS_FEEDS:
        try:
            print(f"📡 Checking {feed['user']}...")
            response = requests.get(feed['url'], timeout=20)
            response.raise_for_status()
            
            # مدیریت فیدهای JSON (مثل RSS.app)
            if feed['url'].endswith('.json'):
                items = response.json().get('items', [])[:5]
                for item in items:
                    post_id = str(item.get('id'))
                    if post_id not in sent_posts:
                        msg = f"📣 *{feed['user']}*:\n\n{item.get('title')}\n\n🔗 [Link]({item.get('url')})\n⏰ {now_str}"
                        send_to_bale(msg)
                        sent_posts.append(post_id)
                        new_found = True
            
            # مدیریت فیدهای XML استاندارد
            else:
                root = ET.fromstring(response.content)
                for item in root.findall("./channel/item")[:5]:
                    link = item.find("link").text
                    if link not in sent_posts:
                        title = item.find("title").text
                        msg = f"📣 *{feed['user']}*:\n\n{title}\n\n🔗 [Link]({link})\n⏰ {now_str}"
                        send_to_bale(msg)
                        sent_posts.append(link)
                        new_found = True
                        
        except Exception as e:
            print(f"⚠️ Error checking {feed['user']}: {e}")

    # ذخیره و نگه داشتن فقط ۱۰۰ مورد آخر برای سبک ماندن دیتابیس
    if new_found:
        with open(sent_file, "w") as f:
            json.dump(sent_posts[-100:], f, indent=4)
        print("✅ Database updated.")
    else:
        print("ℹ️ No new tweets found.")

if __name__ == "__main__":
    main()
