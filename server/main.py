from fastapi import FastAPI, Request, Form, BackgroundTasks, status, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict
from datetime import datetime, timedelta
import secrets
import database
import json
import sqlite3

app = FastAPI()

# DELETE endpoint
@app.delete("/api/delete/{hostname}")
def delete_by_hostname(hostname: str):
    conn = sqlite3.connect("server.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reports WHERE hostname = ?", (hostname,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()

    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Hostname not found")

    return {"message": f"{rows_affected} rows deleted"}

# سایر تنظیمات
app.mount("/static", StaticFiles(directory="./static"), name="static")
templates = Jinja2Templates(directory="./templates")

last_report_time: Dict[str, datetime] = {}
commands: Dict[str, str] = {}

@app.on_event("startup")
def startup():
    database.init_db()

def is_authenticated(request: Request) -> bool:
    return request.cookies.get("auth") == "true"

@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login", response_class=HTMLResponse)
def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    user = database.get_user(username)
    if user and secrets.compare_digest(password, user[1]):
        response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
        response.set_cookie("auth", "true", httponly=True)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "نام کاربری یا رمز اشتباه است"})

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    if not is_authenticated(request):
        return RedirectResponse("/login")

    clients = database.get_latest_reports()
    now = datetime.utcnow()
    for host in clients:
        last_time = last_report_time.get(host)
        clients[host]["status"] = "online" if last_time and (now - last_time).total_seconds() <= 30 else "offline"

    return templates.TemplateResponse("dashboard.html", {"request": request, "clients": clients})

@app.post("/report")
def report(info: dict, background_tasks: BackgroundTasks):
    hostname = info.get("hostname", "unknown")
    background_tasks.add_task(database.insert_report, info)
    last_report_time[hostname] = datetime.utcnow()
    return {"status": "received"}

@app.get("/api/clients")
def api_clients():
    raw_clients = database.get_latest_reports()
    now = datetime.utcnow()
    result = {}

    for host, info in raw_clients.items():
        last_time = last_report_time.get(host)
        status = "online" if last_time and (now - last_time).total_seconds() <= 30 else "offline"

        additional_info = info.get("additional_info", {})
        if isinstance(additional_info, str):
            try:
                additional_info = json.loads(additional_info)
            except:
                additional_info = {}

        result[host] = {
            "status": status,
            "cpu": info.get("cpu"),
            "memory": info.get("memory"),
            "disk": info.get("disk") or additional_info.get("disk"),
            "platform": additional_info.get("platform"),
            "uptime": additional_info.get("uptime")
        }

    return JSONResponse(result)

@app.get("/api/history/{hostname}")
def api_history(hostname: str):
    rows = database.get_history(hostname)
    history = []
    for timestamp, cpu, memory, disk in rows:
        history.append({
            "timestamp": timestamp,
            "cpu": cpu,
            "memory": memory,
            "disk": disk
        })
    return JSONResponse(history)

@app.post("/api/command/{hostname}")
def post_command(hostname: str, command: str):
    commands[hostname] = command
    return {"status": "command sent"}

@app.get("/api/command/{hostname}")
def get_command(hostname: str):
    return {"command": commands.pop(hostname, None)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
