import os
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz

BOT_TOKEN = os.getenv("BALE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# لیست برخی اکانت‌های مهم یا جستجوی خاص (به جای جستجوی کل توییتر)
# چون RSS برای جستجوی کل کمی سخت است، از چند اکانت پرطرفدار شروع می‌کنیم
ACCOUNTS = ["Vahid", "farnood", "jady", "shahin_milani"] 

BALE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"

def load_sent():
    if os.path.exists("sent.json"):
        with open("sent.json", "r") as f:
            return json.load(f)
    return []

def save_sent(data):
    with open("sent.json", "w") as f:
        json.dump(data[-100:], f) # فقط 100 تای آخر را نگه دار

def send_to_bale(text):
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(BALE_URL, json=payload, timeout=15)
    except Exception as e:
        print(f"Error sending to Bale: {e}")

def main():
    sent = load_sent()
    tehran = pytz.timezone("Asia/Tehran")
    
    for user in ACCOUNTS:
        # استفاده از یک Instance عمومی نیتر
        url = f"https://nitter.net/{user}/rss"
        try:
            response = requests.get(url, timeout=20)
            if response.status_code != 200: continue
            
            root = ET.fromstring(response.content)
            for item in root.findall("./channel/item")[:3]: # بررسی 3 توییت آخر هر شخص
                link = item.find("link").text
                tweet_id = link.split("/")[-1].split("#")[0]
                
                if tweet_id not in sent:
                    title = item.find("title").text
                    date_str = datetime.now(tehran).strftime("%H:%M")
                    
                    msg = (
                        f"🐦 *توییت جدید از {user}*\n\n"
                        f"{title}\n\n"
                        f"🔗 [نمایش در توییتر]({link.replace('nitter.net', 'twitter.com')})\n"
                        f"⏰ {date_str}"
                    )
                    
                    send_to_bale(msg)
                    sent.append(tweet_id)
        except Exception as e:
            print(f"Failed for {user}: {e}")
            
    save_sent(sent)

if __name__ == "__main__":
    main()
