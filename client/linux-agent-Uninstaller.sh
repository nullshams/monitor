#!/bin/bash

SERVICE_NAME="sys-agent"
AGENT_DIR="/opt/sys-agent"

echo "🧹 حذف Agent مانیتورینگ..."

# بررسی دسترسی root
if [[ "$EUID" -ne 0 ]]; then
  echo "⚠️ لطفاً اسکریپت را با sudo اجرا کنید."
  exit 1
fi

# توقف و غیرفعالسازی سرویس
echo "🛑 توقف و حذف سرویس systemd..."
systemctl stop $SERVICE_NAME
systemctl disable $SERVICE_NAME
rm -f /etc/systemd/system/$SERVICE_NAME.service
systemctl daemon-reload

# حذف فایل‌ها
echo "🗑️ حذف فایل‌های Agent از $AGENT_DIR"
rm -rf "$AGENT_DIR"

echo "✅ Agent به طور کامل حذف شد."

