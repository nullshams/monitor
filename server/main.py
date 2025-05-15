from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from typing import Dict
import secrets

app = FastAPI()
security = HTTPBasic()
client_data: Dict[str, dict] = {}

# نصب مسیر فایل‌های استاتیک و قالب‌ها
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory=".")

# یوزر و پسورد داشبورد
USERNAME = "admin"
PASSWORD = "1234"

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
async def report(info: dict):
    hostname = info.get("hostname", "unknown")
    client_data[hostname] = info
    return {"status": "received"}

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, username: str = Depends(get_current_user)):
    return templates.TemplateResponse("server/dashboard.html", {
        "request": request,
        "clients": client_data
    })
