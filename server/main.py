from fastapi import FastAPI, Request, Depends, HTTPException, status, BackgroundTasks, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict
import secrets
from datetime import datetime, timedelta
import database

app = FastAPI()

app.mount("/static", StaticFiles(directory="./static"), name="static")
templates = Jinja2Templates(directory="./templates")

last_report_time: Dict[str, datetime] = {}

@app.on_event("startup")
def startup_event():
    database.init_db()

def is_authenticated(request: Request) -> bool:
    return request.cookies.get("auth") == "true"

@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    user = database.get_user(username)
    if user and secrets.compare_digest(password, user[1]):
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="auth", value="true", httponly=True)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "نام کاربری یا رمز عبور اشتباه است"})

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")

    clients = database.get_latest_reports()
    now = datetime.utcnow()
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

@app.post("/report")
async def report(info: dict, background_tasks: BackgroundTasks):
    hostname = info.get("hostname", "unknown")
    background_tasks.add_task(database.insert_report, info)
    last_report_time[hostname] = datetime.utcnow()
    return {"status": "received"}

@app.get("/api/clients")
def get_clients():
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
def get_history(hostname: str):
    rows = database.get_history(hostname)
    history = []
    for timestamp, cpu, memory in rows:
        history.append({
            "timestamp": timestamp,
            "cpu": cpu,
            "memory": memory
        })
    return JSONResponse(content=history)

commands: Dict[str, str] = {}

@app.post("/api/command/{hostname}")
def send_command(hostname: str, command: str):
    commands[hostname] = command
    return {"status": "command sent"}

@app.get("/api/command/{hostname}")
def get_command(hostname: str):
    cmd = commands.pop(hostname, None)
    return {"command": cmd}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
