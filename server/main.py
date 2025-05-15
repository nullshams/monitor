from fastapi import FastAPI, Request, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from typing import Dict
import secrets
import uvicorn
from datetime import datetime, timedelta
from server import database

app = FastAPI()
security = HTTPBasic()

app.mount("/static", StaticFiles(directory="server/static"), name="static")
templates = Jinja2Templates(directory="server/templates")

USERNAME = "admin"
PASSWORD = "1234"

# نگه داشتن آخرین زمان گزارش برای هر کلاینت
last_report_time: Dict[str, datetime] = {}

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.post("/report")
async def report(info: dict, background_tasks: BackgroundTasks):
    hostname = info.get("hostname", "unknown")
    database.insert_report(info)
    last_report_time[hostname] = datetime.utcnow()
    return {"status": "received"}

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, username: str = Depends(get_current_user)):
    clients = database.get_latest_reports()
    now = datetime.utcnow()
    # اضافه کردن وضعیت آنلاین/آفلاین به هر کلاینت
    for host in clients:
        last_time = last_report_time.get(host)
        if not last_time or (now - last_time) > timedelta(seconds=30):
            clients[host]["status"] = "offline"
        else:
            clients[host]["status"] = "online"
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "clients": clients
    })

@app.get("/api/clients")
def get_clients(username: str = Depends(get_current_user)):
    clients = database.get_latest_reports()
    now = datetime.utcnow()
    for host in clients:
        last_time = last_report_time.get(host)
        if not last_time or (now - last_time) > timedelta(seconds=30):
            clients[host]["status"] = "offline"
        else:
            clients[host]["status"] = "online"
    return JSONResponse(content=clients)

@app.get("/api/history/{hostname}")
def get_history(hostname: str, username: str = Depends(get_current_user)):
    rows = database.get_history(hostname)
    history = []
    for timestamp, cpu, memory in rows:
        history.append({
            "timestamp": timestamp,
            "cpu": cpu,
            "memory": memory
        })
    return JSONResponse(content=history)

# API برای ارسال دستور به کلاینت
commands: Dict[str, str] = {}

@app.post("/api/command/{hostname}")
def send_command(hostname: str, command: str, username: str = Depends(get_current_user)):
    commands[hostname] = command
    return {"status": "command sent"}

@app.get("/api/command/{hostname}")
def get_command(hostname: str):
    cmd = commands.pop(hostname, None)
    return {"command": cmd}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
