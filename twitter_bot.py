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

# لیست اکانت‌های فعال برای تست (مطمئن شو آیدی‌ها درست هستند)
ACCOUNTS = ["elonmusk", "virgool_io", "jadidat"] 

# اینستنس‌های جایگزین نیتر
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.moomoo.me",
    "https://nitter.it"
]

def send_to_bale(text):
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(BALE_URL, json=payload, timeout=10)
    except:
        pass

def main():
    # پیام شروع عملیات (اختیاری - می‌توانی بعدا حذف کنی)
    tehran = pytz.timezone("Asia/Tehran")
    now = datetime.now(tehran).strftime("%H:%M")
    
    # لود کردن دیتابیس کوچک توییت‌های قبلی
    sent_file = "sent.json"
    if os.path.exists(sent_file):
        with open(sent_file, "r") as f:
            try:
                sent = json.load(f)
            except:
                sent = []
    else:
        sent = []

    found_any = False
    for user in ACCOUNTS:
        for instance in NITTER_INSTANCES:
            url = f"{instance}/{user}/rss"
            try:
                print(f"Searching {user} via {instance}...")
                response = requests.get(url, timeout=15)
                if response.status_code != 200:
                    continue
                
                root = ET.fromstring(response.content)
                items = root.findall("./channel/item")
                
                for item in items[:3]: # بررسی ۳ توییت آخر
                    link = item.find("link").text
                    tweet_id = link.split("/")[-1].split("#")[0]
                    
                    if tweet_id not in sent:
                        title = item.find("title").text
                        # حذف نام یوزر از ابتدای تایتل اگر وجود داشت
                        clean_title = title.split(":")[-1] if ":" in title else title
                        
                        msg = (
                            f"📣 *توییت جدید از {user}*\n"
                            f"━━━━━━━━━━━━━━\n"
                            f"{clean_title.strip()}\n\n"
                            f"🔗 [مشاهده در توییتر]({link.replace(instance, 'https://twitter.com')})\n"
                            f"⏰ {now}"
                        )
                        send_to_bale(msg)
                        sent.append(tweet_id)
                        found_any = True
                
                if items: break # اگر با این اینستنس موفق شد، برو سراغ اکانت بعدی
            except Exception as e:
                print(f"Error: {e}")

    # ذخیره آیدی‌های جدید
    with open(sent_file, "w") as f:
        json.dump(sent[-100:], f)

    if not found_any:
        print("No new tweets found in this run.")

if __name__ == "__main__":
    main()
