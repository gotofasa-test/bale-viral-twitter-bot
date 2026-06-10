import os
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz

BOT_TOKEN = os.getenv("BALE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
BALE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"

# لیست فیدهای RSS معتبر (جایگزین مستقیم اکانت‌های توییتر)
# تو می‌توانی از سایت rss.app برای هر اکانتی که بخواهی لینک بسازی
RSS_FEEDS = [
    {"user": "ElonMusk", "url": "https://rss.app/feeds/v1.1/t6L6IByu9pT38G6K.json"}, # مثال JSON Feed
    {"user": "TechCrunch", "url": "https://techcrunch.com/feed/"} # برای تست محتوا
]

def send_to_bale(text):
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(BALE_URL, json=payload, timeout=10)

def main():
    tehran = pytz.timezone("Asia/Tehran")
    now = datetime.now(tehran).strftime("%H:%M")
    
    sent_file = "sent.json"
    if os.path.exists(sent_file):
        with open(sent_file, "r") as f:
            try: sent = json.load(f)
            except: sent = []
    else:
        sent = []

    new_tweets_found = 0
    
    for feed in RSS_FEEDS:
        try:
            print(f"📡 Checking {feed['user']}...")
            response = requests.get(feed['url'], timeout=20)
            
            if response.status_code == 200:
                # اگر فید JSON بود (مثل RSS.app)
                if feed['url'].endswith('.json'):
                    data = response.json()
                    for item in data.get('items', [])[:3]:
                        item_id = str(item.get('id'))
                        if item_id not in sent:
                            title = item.get('title', 'No Title')
                            link = item.get('url', '')
                            msg = f"📣 *{feed['user']}*:\n\n{title}\n\n🔗 [Link]({link})\n⏰ {now}"
                            send_to_bale(msg)
                            sent.append(item_id)
                            new_tweets_found += 1
                # اگر فید XML بود
                else:
                    root = ET.fromstring(response.content)
                    for item in root.findall("./channel/item")[:3]:
                        link = item.find("link").text
                        if link not in sent:
                            title = item.find("title").text
                            msg = f"📣 *{feed['user']}*:\n\n{title}\n\n🔗 [Link]({link})\n⏰ {now}"
                            send_to_bale(msg)
                            sent.append(link)
                            new_tweets_found += 1
            else:
                print(f"⚠️ Error {response.status_code} for {feed['user']}")
        except Exception as e:
            print(f"❌ Failed: {e}")

    with open(sent_file, "w") as f:
        json.dump(sent[-100:], f)

    # پیام وضعیت برای مجید
    if new_tweets_found == 0:
        send_to_bale(f"🔍 وضعیت: سیستم متصل است اما محتوای جدیدی در فیدها یافت نشد.\n⏰ {now}")

if __name__ == "__main__":
    main()
