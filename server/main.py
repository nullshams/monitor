# monitoring-system/server/main.py

from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.status import HTTP_401_UNAUTHORIZED
import uvicorn
import secrets
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="./static"), name="static")

security = HTTPBasic()

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"

client_data = {}

# احراز هویت ساده

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.post("/report")
async def report(info: dict):
    hostname = info.get("hostname", "unknown")
    client_data[hostname] = info
    return {"status": "received"}

@app.get("/", response_class=HTMLResponse)
async def dashboard(username: str = Depends(authenticate)):
    html = """
    <html><head><title>Dashboard</title>
    <link rel='stylesheet' href='/static/style.css'>
    </head><body>
    <h1>Monitoring Dashboard</h1>
    <div class='container'>
    """
    for host, data in client_data.items():
        html += f"""
        <div class='card'>
            <h2>{host}</h2>
            <p><strong>CPU:</strong> {data['cpu']}%</p>
            <p><strong>Memory:</strong> {data['memory']}%</p>
            <p><strong>Disk:</strong> {data['disk']}%</p>
        </div>
        """
    html += "</div></body></html>"
    return html

if __name__ == "__main__":
    os.makedirs("server/static", exist_ok=True)
    with open("server/static/style.css", "w") as f:
        f.write("""
        body {
            font-family: Arial, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        h1 {
            text-align: center;
        }
        .container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .card {
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        """)

    uvicorn.run(app, host="0.0.0.0", port=8000)
