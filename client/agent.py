import psutil
import socket
import requests
import time

def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    }

def discover_server(timeout=5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)

    message = b"DISCOVER_SERVER"
    sock.sendto(message, ('<broadcast>', 5005))

    try:
        data, addr = sock.recvfrom(1024)
        server_ip = data.decode()
        print(f"✅ سرور پیدا شد: {server_ip}")
        return server_ip
    except socket.timeout:
        print("❌ سرور پیدا نشد.")
        return None

def send_data(server_url):
    data = get_system_info()
    try:
        response = requests.post(server_url, json=data)
        print("Sent:", response.status_code)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    server_ip = discover_server()
    if not server_ip:
        exit(1)

    SERVER_URL = f"http://{server_ip}:8000/report"

    while True:
        send_data(SERVER_URL)
        time.sleep(30)
