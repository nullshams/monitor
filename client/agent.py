import psutil
import socket
import requests
import time

SERVER_URL = "http://192.168.1.104:8000/report"  # IP سرور خودتو اینجا بذار

def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    }

def send_data():
    data = get_system_info()
    try:
        response = requests.post(SERVER_URL, json=data)
        print("Sent:", response.status_code)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    while True:
        send_data()
        time.sleep(30)
