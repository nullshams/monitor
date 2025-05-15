import sqlite3
from typing import List, Tuple, Optional

DATABASE = "server.db"

def get_connection():
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

conn = get_connection()

def init_db():
    conn.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostname TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        cpu REAL,
        memory REAL,
        additional_info TEXT
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)
    conn.commit()
    # اضافه کردن یک کاربر پیش‌فرض (admin / 1234) اگر هنوز وجود نداشته باشد
    cur = conn.execute("SELECT * FROM users WHERE username = ?", ("admin",))
    if not cur.fetchone():
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "1234"))
        conn.commit()

def insert_report(data: dict):
    hostname = data.get("hostname", "unknown")
    timestamp = data.get("timestamp") or ""
    cpu = data.get("cpu")
    memory = data.get("memory")
    additional_info = str(data.get("additional_info", ""))

    if not timestamp:
        from datetime import datetime
        timestamp = datetime.utcnow().isoformat()

    conn.execute("""
        INSERT INTO reports (hostname, timestamp, cpu, memory, additional_info)
        VALUES (?, ?, ?, ?, ?)
    """, (hostname, timestamp, cpu, memory, additional_info))
    conn.commit()

def get_latest_reports() -> dict:
    query = """
    SELECT r1.hostname, r1.timestamp, r1.cpu, r1.memory, r1.additional_info
    FROM reports r1
    INNER JOIN (
        SELECT hostname, MAX(timestamp) as max_ts
        FROM reports
        GROUP BY hostname
    ) r2 ON r1.hostname = r2.hostname AND r1.timestamp = r2.max_ts
    """
    rows = conn.execute(query).fetchall()
    results = {}
    for row in rows:
        results[row["hostname"]] = {
            "timestamp": row["timestamp"],
            "cpu": row["cpu"],
            "memory": row["memory"],
            "additional_info": row["additional_info"]
        }
    return results

def get_history(hostname: str) -> List[Tuple[str, float, float]]:
    rows = conn.execute(
        "SELECT timestamp, cpu, memory FROM reports WHERE hostname = ? ORDER BY timestamp DESC LIMIT 100",
        (hostname,)
    ).fetchall()
    return [(r["timestamp"], r["cpu"], r["memory"]) for r in rows]

def get_user(username: str) -> Optional[Tuple[str, str]]:
    """یوزرنیم و پسورد را از دیتابیس می‌گیرد"""
    row = conn.execute("SELECT username, password FROM users WHERE username = ?", (username,)).fetchone()
    if row:
        return (row["username"], row["password"])
    return None
