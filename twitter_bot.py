import os
import json
import requests
from datetime import datetime
import pytz

# تنظیمات محیطی از GitHub Secrets
BOT_TOKEN = os.getenv("BALE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
BALE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"

# فیدهای هدف
RSS_FEEDS = [
    {"user": "jacksonhinkle", "url": "https://rss.app/feeds/v1.1/nQRfNkiu3xqp5UPX.json"},
    {"user": "Khamenei_fa", "url": "https://rss.app/feeds/v1.1/cxDtmcWC56oBdtTe.json"}
]

def send_to_bale(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Missing Bale Credentials")
        return
    
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        res = requests.post(BALE_URL, json=payload, timeout=15)
        res.raise_for_status()
        print("✅ Message successfully sent to Bale")
    except Exception as e:
        print(f"❌ Failed to send to Bale: {e}")

def load_sent_posts(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def main():
    print("🚀 Bot Started...")
    tehran = pytz.timezone("Asia/Tehran")
    now_str = datetime.now(tehran).strftime("%H:%M")
    sent_file = "sent.json"
    sent_posts = load_sent_posts(sent_file)
    new_found = False

    for feed in RSS_FEEDS:
        print(f"📡 Checking feed for: {feed['user']}")
        try:
            response = requests.get(feed['url'], timeout=20)
            response.raise_for_status()
            
            # پردازش JSON (RSS.app)
            items = response.json().get('items', [])[:5]
            for item in items:
                post_id = str(item.get('id', item.get('url')))
                if post_id not in sent_posts:
                    title = item.get('title', 'No Title')
                    link = item.get('url', '')
                    msg = f"📣 *{feed['user']}*:\n\n{title}\n\n🔗 [Link]({link})\n⏰ {now_str}"
                    
                    send_to_bale(msg)
                    sent_posts.append(post_id)
                    new_found = True
        except Exception as e:
            print(f"⚠️ Error checking {feed['user']}: {e}")

    if new_found:
        # نگهداری ۱۰۰ آی‌دی آخر برای جلوگیری از سنگین شدن فایل
        with open(sent_file, "w") as f:
            json.dump(sent_posts[-100:], f)
        print("✅ Database updated with new posts.")
    else:
        print("ℹ️ No new tweets found in this run.")

if __name__ == "__main__":
    main()
