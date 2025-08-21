# 🖥️ System Monitoring System

یک پلتفرم مانیتورینگ سیستم به‌صورت real-time با استفاده از **FastAPI** برای سرور و **Python agents** برای کلاینت‌ها.

---
![نمای داشبورد](image/dark.png)
![نمای داشبورد](image/light.png)

## ✨ امکانات

### ✅ Server (Backend)

- جمع‌آوری اطلاعات CPU، RAM، دیسک و uptime از کلاینت‌ها  
- داشبورد تعاملی راست‌چین (RTL) با به‌روزرسانی زنده  
- کنترل از راه دور:shutdown`, `restart` `  
- مشاهده‌ی تاریخچه لاگ‌های هر کلاینت  
- احراز هویت کاربران با SQLite  

### 🛰️ Agent (Client)

- ارسال گزارش دوره‌ای به سرور (هر 10 ثانیه)  
- دریافت و اجرای دستورات سرور  
- استفاده از `psutil`، `requests` و `espeak` برای تعامل با سیستم  
- اجرا به صورت systemd service (در لینوکس)  
- کاملاً ایزوله‌شده با استفاده از `venv`  

---

## ⚙️ پیش‌نیازها

- Python 3.8+
- pip  
- در لینوکس: نصب پکیج `espeak`  
- در ویندوز: PowerShell نسخه 5 یا بالاتر  

---

## 🧭 نصب سرور (Linux / Windows)

```bash
git clone https://github.com/nullshams/monitor.git
cd monitor
```

### (اختیاری) ایجاد محیط مجازی:

```bash
python -m venv venv
source venv/bin/activate  # ویندوز: venv\Scripts\activate
```

### نصب وابستگی‌ها:

```bash
pip install -r requirements.txt
```

### مقداردهی اولیه دیتابیس:

```bash
python -c "import database; database.init_db()"
```

### ایجاد کاربر ادمین:

```bash
python -c "import database; database.add_user('admin', 'yourpassword')"
```

### اجرای سرور:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🐧 نصب Agent (Linux)

```bash
cd client
chmod +x install-agent.sh
sudo ./install-agent.sh
```

- آدرس سرور را وارد کنید (مثلاً: `http://192.168.1.10:8000`)  
- به صورت systemd service اجرا می‌شود  
- محیط مجازی ساخته و پکیج‌ها نصب می‌شوند  

### بررسی وضعیت سرویس:

```bash
systemctl status sys-agent
```

### حذف کامل Agent:

```bash
sudo ./uninstall-agent.sh
```

---

## 🪟 نصب Agent (Windows)

1. اجرای PowerShell با دسترسی Administrator  
2. اجرای نصب‌کننده:

```powershell
.\install-agent.ps1
```

- ساخت venv  
- نصب پکیج‌ها  
- ثبت اجرای خودکار در Startup با Task Scheduler  

### حذف Agent:

```powershell
.\uninstall-agent.ps1
```

---

## 📁 ساختار پروژه

```
monitor/
├── main.py              # سرور FastAPI
├── database.py          # مدیریت SQLite و کاربران
├── templates/           # فایل‌های HTML داشبورد
├── static/              # CSS 
├── client/
│   ├── agent.py
│   ├── install-agent.sh
│   ├── uninstall-agent.sh
│   ├── install-agent.ps1
│   └── uninstall-agent.ps1
└── requirements.txt
```

---

## 🔗 آدرس‌های پیش‌فرض

- داشبورد: [http://localhost:8000](http://localhost:8000)  
- ورود: [http://localhost:8000/login](http://localhost:8000/login)  
- API REST: `/api/...`

---

## ⏱️ نکات مهم

- کلاینت‌ها هر 10 ثانیه گزارش ارسال می‌کنند  
- اگر کلاینت تا 30 ثانیه گزارشی ارسال نکند، به عنوان "آفلاین" نشان داده می‌شود  
- تمام اطلاعات در فایل `server.db` ذخیره می‌شود  

---

## 🔧 اجرای سرور در پس‌زمینه (Linux)

```bash
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > log.txt 2>&1 &
```

همچنین می‌توانید از `systemd`، `supervisor` یا `pm2` استفاده کنید.

---

## 📜 License

پروژه تحت لایسنس MIT منتشر شده است.
