import platform
import psutil
import socket
import time
import requests
import os
from datetime import datetime

SERVER_URL = "http://192.168.1.104:8000"  # آدرس سرور را در صورت نیاز تغییر بده
REPORT_INTERVAL = 10  # ثانیه
COMMAND_CHECK_INTERVAL = 5  # ثانیه

def get_system_info():
    hostname = socket.gethostname()
    try:
        cpu = psutil.cpu_percent(interval=1)
    except Exception:
        cpu = None

    try:
        memory = psutil.virtual_memory().percent
    except Exception:
        memory = None

    try:
        disk = psutil.disk_usage("/").percent
    except Exception:
        disk = None

    platform_info = platform.system() + " " + platform.release()

    return {
        "hostname": hostname,
        "timestamp": datetime.utcnow().isoformat(),
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
        "additional_info": {
            "platform": platform_info,
            "ip": socket.gethostbyname(hostname),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
        }
    }

def execute_command(command):
    if command == "restart":
        if platform.system() == "Windows":
            os.system("shutdown /r /t 1")
        else:
            os.system("sudo reboot")

def main():
    hostname = socket.gethostname()
    last_report_time = 0
    last_command_check = 0

    while True:
        current_time = time.time()

        # ارسال گزارش
        if current_time - last_report_time > REPORT_INTERVAL:
            info = get_system_info()
            try:
                requests.post(f"{SERVER_URL}/report", json=info, timeout=5)
            except:
                pass
            last_report_time = current_time

        # بررسی دستورات
        if current_time - last_command_check > COMMAND_CHECK_INTERVAL:
            try:
                res = requests.get(f"{SERVER_URL}/api/command/{hostname}", timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    cmd = data.get("command")
                    if cmd:
                        execute_command(cmd)
            except:
                pass
            last_command_check = current_time

        time.sleep(1)

if __name__ == "__main__":
    main()
