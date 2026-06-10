import os
import json
import requests
import snscrape.modules.twitter as sntwitter
from datetime import datetime
import pytz

BOT_TOKEN = os.getenv("BALE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

QUERY = "lang:fa min_faves:200"

BALE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"


def load_sent():
    try:
        with open("sent.json", "r") as f:
            return json.load(f)
    except:
        return []


def save_sent(data):
    with open("sent.json", "w") as f:
        json.dump(data, f)


def send_message(text):
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }

    r = requests.post(BALE_URL, json=payload, timeout=20)
    r.raise_for_status()


def build_message(tweet):
    tehran = pytz.timezone("Asia/Tehran")
    now = datetime.now(tehran).strftime("%Y-%m-%d %H:%M")

    msg = (
        f"🔥 *توییت وایرال فارسی*\n\n"
        f"👤 {tweet.user.username}\n\n"
        f"{tweet.content}\n\n"
        f"❤️ {tweet.likeCount}   🔁 {tweet.retweetCount}\n\n"
        f"🔗 {tweet.url}\n\n"
        f"🕒 {now}"
    )

    return msg


def main():

    sent = load_sent()

    tweets = []

    for tweet in sntwitter.TwitterSearchScraper(QUERY).get_items():
        if tweet.id not in sent:
            score = tweet.likeCount + tweet.retweetCount

            if score > 300:
                tweets.append(tweet)

        if len(tweets) >= 5:
            break

    for tweet in tweets:

        message = build_message(tweet)

        send_message(message)

        sent.append(tweet.id)

    save_sent(sent)


if __name__ == "__main__":
    main()
