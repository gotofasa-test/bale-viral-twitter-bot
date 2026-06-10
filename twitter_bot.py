import os
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz

BOT_TOKEN = os.getenv("BALE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
BALE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"

# لیست اینستنس‌هایی که طبق آخرین گزارش‌ها فعال‌تر هستند
NITTER_INSTANCES = [
    "https://nitter.poast.org",
    "https://nitter.privacydev.net",
    "https://nitter.no-logs.com",
    "https://nitter.projectsegfau.lt"
]

ACCOUNTS = ["Twitter", "SpaceX", "NASA", "Github"]

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
    
    for user in ACCOUNTS:
        for instance in NITTER_INSTANCES:
            url = f"{instance}/{user}/rss"
            try:
                print(f"📡 Testing {user} on {instance}...")
                response = requests.get(url, timeout=20)
                
                if response.status_code == 200 and len(response.content) > 500:
                    root = ET.fromstring(response.content)
                    items = root.findall("./channel/item")
                    
                    for item in items[:2]:
                        link = item.find("link").text
                        tweet_id = link.split("/")[-1].split("#")[0]
                        
                        if tweet_id not in sent:
                            title = item.find("title").text
                            msg = f"🐦 *{user}*:\n\n{title[:300]}\n\n🔗 [Link]({link.replace(instance, 'https://twitter.com')})\n⏰ {now}"
                            send_to_bale(msg)
                            sent.append(tweet_id)
                            new_tweets_found += 1
                    print(f"✅ Success with {instance}")
                    break # اگر برای این کاربر جواب گرفت، برو سراغ کاربر بعدی
                else:
                    print(f"⚠️ {instance} returned empty or error {response.status_code}")
            except Exception as e:
                print(f"❌ {instance} failed: {e}")

    # ذخیره دیتابیس
    with open(sent_file, "w") as f:
        json.dump(sent[-100:], f)

    # پیام وضعیت برای مجید (فقط برای اطمینان از کارکرد - بعدا حذفش کن)
    if new_tweets_found == 0:
        send_to_bale(f"🔍 چک شد، اما توییت جدیدی پیدا نشد.\n⏰ {now}")

if __name__ == "__main__":
    main()
