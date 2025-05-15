# server/database.py
import sqlite3
from datetime import datetime

conn = sqlite3.connect("clients.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hostname TEXT,
    platform TEXT,
    cpu REAL,
    memory REAL,
    disk REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

def insert_report(info: dict):
    cursor.execute("""
        INSERT INTO reports (hostname, platform, cpu, memory, disk)
        VALUES (?, ?, ?, ?, ?)
    """, (
        info.get("hostname"),
        info.get("platform"),
        info.get("cpu"),
        info.get("memory"),
        info.get("disk")
    ))
    conn.commit()

def get_latest_reports():
    cursor.execute("""
        SELECT hostname, platform, cpu, memory, disk, MAX(timestamp)
        FROM reports
        GROUP BY hostname
    """)
    rows = cursor.fetchall()
    result = {}
    for row in rows:
        result[row[0]] = {
            "platform": row[1],
            "cpu": row[2],
            "memory": row[3],
            "disk": row[4],
            "timestamp": row[5]
        }
    return result

def get_history(hostname: str, limit=30):
    cursor.execute("""
        SELECT timestamp, cpu, memory
        FROM reports
        WHERE hostname = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (hostname, limit))
    rows = cursor.fetchall()
    return rows[::-1]  # معکوس برای نمایش از قدیم به جدید
