import requests
import json
import os
from datetime import datetime
from flask import Flask
import threading
import time

USERNAME = 'xxxibgdrgn'
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

def get_following(username):
    url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        try:
            data = res.json()
            return data['graphql']['user']['edge_follow']['count']
        except Exception as e:
            print("Lỗi đọc JSON:", e)
    else:
        print("Lỗi HTTP:", res.status_code)
    return None

def send_telegram(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': message}
    res = requests.post(url, data=payload)
    if not res.ok:
        print("Lỗi Telegram:", res.text)

def track():
    try:
        with open('following.json', 'r') as f:
            data = json.load(f)
    except:
        data = {}

    current = get_following(USERNAME)
    previous = data.get('following')

    if current is None:
        print("Không lấy được số following. Bỏ qua.")
    else:
        if previous is None:
            send_telegram(f"👁‍🗨 Theo dõi bắt đầu: @{USERNAME} đang theo dõi {current} tài khoản.")
        elif current != previous:
            delta = current - previous
            send_telegram(f"🔔 @{USERNAME} thay đổi số following:\n{previous} → {current} ({'+' if delta > 0 else ''}{delta})")

        data['following'] = current
        data['last_checked'] = datetime.now().isoformat()
        with open('following.json', 'w') as f:
            json.dump(data, f, indent=2)

# Flask app để giữ Replit luôn sống
app = Flask(__name__)

@app.route('/')
def home():
    return "Instagram Following Tracker is Running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    track()
    while True:
        time.sleep(600)  # chạy lại mỗi 10 phút
        track()
