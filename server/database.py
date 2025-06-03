# database.py
import sqlite3
import json
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
        disk REAL,
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
    if not conn.execute("SELECT * FROM users WHERE username = ?", ("admin",)).fetchone():
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "1234"))
        conn.commit()

def insert_report(data: dict):
    hostname = data.get("hostname", "unknown")
    timestamp = data.get("timestamp") or ""
    cpu = data.get("cpu")
    memory = data.get("memory")
    disk = data.get("disk")
    additional_info = json.dumps(data.get("additional_info", {}))

    conn.execute("""
        INSERT INTO reports (hostname, timestamp, cpu, memory, disk, additional_info)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (hostname, timestamp, cpu, memory, disk, additional_info))
    conn.commit()

def get_latest_reports() -> dict:
    query = """
    SELECT r1.hostname, r1.timestamp, r1.cpu, r1.memory, r1.disk, r1.additional_info
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
        additional_info_raw = row["additional_info"]
        try:
            additional_info = json.loads(additional_info_raw) if additional_info_raw else {}
        except json.JSONDecodeError:
            additional_info = {}

        results[row["hostname"]] = {
            "timestamp": row["timestamp"],
            "cpu": row["cpu"],
            "memory": row["memory"],
            "disk": row["disk"],
            "additional_info": additional_info
        }
    return results


def get_history(hostname: str) -> List[Tuple[str, float, float, float]]:
    rows = conn.execute(
        "SELECT timestamp, cpu, memory, disk FROM reports WHERE hostname = ? ORDER BY timestamp DESC LIMIT 100",
        (hostname,)
    ).fetchall()
    return [(r["timestamp"], r["cpu"], r["memory"], r["disk"]) for r in rows]

def get_user(username: str) -> Optional[Tuple[str, str]]:
    row = conn.execute("SELECT username, password FROM users WHERE username = ?", (username,)).fetchone()
    if row:
        return (row["username"], row["password"])
    return None
