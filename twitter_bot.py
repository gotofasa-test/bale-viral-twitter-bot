import os
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz

BOT_TOKEN = os.getenv("BALE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# لیست چند نمونه سالم از نیتر برای تست
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.cz",
    "https://nitter.it",
    "https://nitter.privacydev.net"
]

ACCOUNTS = ["Vahid", "jady"] 

BALE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"

def send_to_bale(text):
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    r = requests.post(BALE_URL, json=payload, timeout=15)
    return r.status_code

def main():
    # ۱. ارسال پیام تست برای اطمینان از اتصال بله
    print("Sending test message to Bale...")
    test_res = send_to_bale("🚀 مجید جان، ربات با موفقیت اجرا شد! در حال جستجوی توییت‌ها...")
    print(f"Bale Test Status: {test_res}")

    if not os.path.exists("sent.json"):
        with open("sent.json", "w") as f: json.dump([], f)

    with open("sent.json", "r") as f: sent = json.load(f)
    
    tehran = pytz.timezone("Asia/Tehran")
    
    for user in ACCOUNTS:
        success = False
        for instance in NITTER_INSTANCES:
            if success: break
            url = f"{instance}/{user}/rss"
            try:
                print(f"Checking {user} on {instance}...")
                response = requests.get(url, timeout=15)
                if response.status_code != 200: continue
                
                root = ET.fromstring(response.content)
                items = root.findall("./channel/item")
                
                for item in items[:2]:
                    link = item.find("link").text
                    tweet_id = link.split("/")[-1].split("#")[0]
                    
                    if tweet_id not in sent:
                        title = item.find("title").text
                        msg = f"🐦 *{user}*:\n\n{title}\n\n🔗 [Link]({link.replace(instance, 'https://twitter.com')})"
                        send_to_bale(msg)
                        sent.append(tweet_id)
                success = True
            except Exception as e:
                print(f"Error on {instance}: {e}")
            
    with open("sent.json", "w") as f:
        json.dump(sent[-100:], f)

if __name__ == "__main__":
    main()
