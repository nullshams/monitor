# agent.py
import platform
import psutil
import socket
import time
import requests
import os
import subprocess
from datetime import datetime

SERVER_URL = os.environ.get("SERVER_URL", "http://192.168.77.163:8000")
REPORT_INTERVAL = 10
COMMAND_CHECK_INTERVAL = 5

def get_system_info():
    hostname = socket.gethostname()
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/" if os.name != "nt" else "C:\\").percent
    uptime = time.time() - psutil.boot_time()
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
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "uptime": int(uptime)
        }
    }

def execute_command(command):
    if command == "restart":
        os.system("shutdown /r /t 1" if platform.system() == "Windows" else "sudo reboot")
    elif command == "shutdown":
        os.system("shutdown /s /t 1" if platform.system() == "Windows" else "sudo poweroff")
    elif command.startswith("run:"):
        cmd = command.split("run:", 1)[1].strip()
        subprocess.Popen(cmd, shell=True)
    elif command.startswith("say:"):
        msg = command.split("say:", 1)[1].strip()
        if platform.system() == "Darwin":
            os.system(f'say "{msg}"')
        elif platform.system() == "Linux":
            os.system(f'espeak "{msg}"')

def main():
    hostname = socket.gethostname()
    last_report_time = 0
    last_command_check = 0

    while True:
        current_time = time.time()

        if current_time - last_report_time > REPORT_INTERVAL:
            info = get_system_info()
            try:
                requests.post(f"{SERVER_URL}/report", json=info, timeout=5)
            except:
                pass
            last_report_time = current_time

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
