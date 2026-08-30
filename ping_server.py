import time
import requests
import sys

# Yahan apni Render website ka URL dalein
RENDER_URL = "https://YOUR-RENDER-APP-NAME.onrender.com/"

print(f"Starting Keep-Alive ping script for: {RENDER_URL}")
print("Press Ctrl+C to stop.")

while True:
    try:
        response = requests.get(RENDER_URL, timeout=15)
        if response.status_code == 200:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Ping successful! Server is awake.")
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Ping sent, but server returned status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Ping failed: {e}")
    
    # 12 minutes (720 seconds) ke baad wapas ping karega
    time.sleep(720)
