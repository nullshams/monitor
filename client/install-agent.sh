#!/bin/bash

AGENT_DIR="/opt/sys-agent"
SERVICE_NAME="sys-agent"
AGENT_FILE="agent.py"
VENV_DIR="$AGENT_DIR/venv"
PYTHON=$(which python3 2>/dev/null || which python 2>/dev/null)

# بررسی وجود Python
if [ -z "$PYTHON" ]; then
    echo "❌ خطا: Python یافت نشد. لطفاً Python 3.8 یا بالاتر را نصب کنید."
    exit 1
fi

echo "🔧 نصب Agent مانیتورینگ"

# تابع اعتبارسنجی URL
validate_url() {
    local url=$1
    # بررسی فرمت URL با پورت (مثلاً http://192.168.1.100:8000 یا https://example.com:443)
    if [[ ! $url =~ ^(http|https)://[a-zA-Z0-9.-]+(:[0-9]{1,5})?$ ]]; then
        echo "❌ خطا: آدرس سرور باید شامل پروتکل (http/https) و پورت باشد (مثلاً http://192.168.1.100:8000)."
        return 1
    fi
    # بررسی وجود پورت
    if [[ ! $url =~ :[0-9]{1,5}$ ]]; then
        echo "❌ خطا: آدرس سرور باید شامل پورت باشد (مثلاً :8000)."
        return 1
    fi
    return 0
}

# تابع بررسی دسترسی به سرور
check_server() {
    local url=$1
    if ! curl --output /dev/null --silent --head --fail "$url" 2>/dev/null; then
        echo "⚠️ هشدار: سرور در $url در دسترس نیست. لطفاً بررسی کنید و دوباره تلاش کنید."
        return 1
    fi
    return 0
}

# گرفتن آدرس سرور از کاربر
while true; do
    read -p "🌐 لطفاً آدرس سرور را وارد کنید (مثلاً http://192.168.1.100:8000): " SERVER_URL
    SERVER_URL=${SERVER_URL:-http://127.0.0.1:8000}  # مقدار پیش‌فرض
    if validate_url "$SERVER_URL"; then
        if check_server "$SERVER_URL"; then
            break
        else
            echo "❌ لطفاً آدرس معتبر دیگری وارد کنید."
            continue
        fi
    else
        echo "❌ لطفاً آدرس را با فرمت صحیح وارد کنید."
        continue
    fi
done

# بررسی دسترسی root
if [[ "$EUID" -ne 0 ]]; then
    echo "⚠️ لطفاً اسکریپت را با sudo اجرا کنید."
    exit 1
fi

# بررسی وجود فایل agent.py
if [ ! -f "$AGENT_FILE" ]; then
    echo "❌ خطا: فایل $AGENT_FILE یافت نشد. لطفاً مطمئن شوید فایل در دایرکتوری فعلی وجود دارد."
    exit 1
fi

# ایجاد محیط مجازی
echo "📦 ایجاد محیط مجازی در $VENV_DIR..."
mkdir -p "$AGENT_DIR"
"$PYTHON" -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# نصب پیش‌نیازها در محیط مجازی
echo "📦 نصب کتابخانه‌های پایتون در محیط مجازی..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install psutil requests

# نصب espeak در لینوکس
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🎤 نصب espeak..."
    apt-get update -qq && apt-get install -y espeak
fi

# کپی Agent
echo "📁 کپی agent به $AGENT_DIR"
cp "$AGENT_FILE" "$AGENT_DIR/"
chmod +x "$AGENT_DIR/$AGENT_FILE"

# ایجاد سرویس systemd
echo "🛠️ ساخت systemd unit"
cat <<EOF > /etc/systemd/system/$SERVICE_NAME.service
[Unit]
Description=System Monitoring Agent
After=network.target

[Service]
Environment=SERVER_URL=$SERVER_URL
ExecStart=$VENV_DIR/bin/python $AGENT_DIR/$AGENT_FILE
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

# فعال‌سازی و راه‌اندازی سرویس
systemctl daemon-reload
systemctl enable $SERVICE_NAME
if systemctl restart $SERVICE_NAME; then
    echo "✅ Agent نصب و فعال شد!"
    echo "📡 متصل به: $SERVER_URL"
else
    echo "❌ خطا در راه‌اندازی سرویس. لطفاً لاگ‌های سیستم را بررسی کنید (journalctl -u $SERVICE_NAME)."
    exit 1
fi
