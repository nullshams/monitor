import platform
import psutil
import socket
import time
import requests
import os
import sys

SERVER_URL = "http://YOUR_SERVER_IP:8000"  # آدرس سرور رو تغییر بده
REPORT_INTERVAL = 10  # ثانیه
COMMAND_CHECK_INTERVAL = 5  # ثانیه

def get_system_info():
    hostname = socket.gethostname()
    return {
        "hostname": hostname,
        "platform": platform.system() + " " + platform.release(),
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
    }

def execute_command(command):
    hostname = socket.gethostname()
    print(f"دریافت دستور: {command}")
    if command == "restart":
        print("در حال ری‌استارت سیستم...")
        if platform.system() == "Windows":
            os.system("shutdown /r /t 1")
        else:
            os.system("sudo reboot")
    else:
        print(f"دستور ناشناخته: {command}")

def main():
    hostname = socket.gethostname()
    last_report_time = 0
    last_command_check = 0

    while True:
        current_time = time.time()

        # ارسال گزارش هر REPORT_INTERVAL ثانیه
        if current_time - last_report_time > REPORT_INTERVAL:
            info = get_system_info()
            try:
                res = requests.post(f"{SERVER_URL}/report", json=info, timeout=5)
                if res.status_code == 200:
                    print(f"گزارش ارسال شد: {info}")
                else:
                    print(f"خطا در ارسال گزارش: {res.status_code}")
            except Exception as e:
                print(f"خطا در ارتباط با سرور: {e}")
            last_report_time = current_time

        # چک کردن دستور جدید هر COMMAND_CHECK_INTERVAL ثانیه
        if current_time - last_command_check > COMMAND_CHECK_INTERVAL:
            try:
                res = requests.get(f"{SERVER_URL}/api/command/{hostname}", timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    cmd = data.get("command")
                    if cmd:
                        execute_command(cmd)
                else:
                    print(f"خطا در دریافت دستور: {res.status_code}")
            except Exception as e:
                print(f"خطا در دریافت دستور: {e}")
            last_command_check = current_time

        time.sleep(1)

if __name__ == "__main__":
    main()
