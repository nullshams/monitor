import platform
import psutil
import requests
import socket
import time

# 🔧 آدرس سرور رو اینجا تنظیم کن (با پورت درست!)
SERVER_URL = "http://192.168.1.104:8000/report"  # ← IP سرور رو اینجا بذار

def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    }

while True:
    try:
        info = get_system_info()
        response = requests.post(SERVER_URL, json=info, timeout=5)
        print(f"Sent to {SERVER_URL} | Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    time.sleep(10)  # هر 10 ثانیه یک بار
