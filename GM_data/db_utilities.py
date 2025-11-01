import sqlite3
import csv
from datetime import datetime
from secret import *


# ========== UTILITY FUNCTIONS ==========


def add_reading(reading, location="ART-BUILDING", confidence=None, image_path=None, status="success", notes=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat(timespec='seconds')

    cursor.execute("""
    INSERT INTO readings (timestamp, reading, location, confidence, image_path, status, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (timestamp, reading, location, confidence, image_path, status, notes))

    conn.commit()
    conn.close()


def get_readings_by_date(date_str):
    """date_str example: '2025-11-01'"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM readings
    WHERE timestamp LIKE ?
    ORDER BY timestamp DESC
    """, (f"{date_str}%",))

    rows = cursor.fetchall()
    conn.close()

    return rows


def update_setting(key, value):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO settings (key, value)
    VALUES (?, ?)
    ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """, (key, str(value)))

    conn.commit()
    conn.close()


def get_setting(key):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return row[0]
    return None


def export_to_csv(date_str, output_path):
    readings = get_readings_by_date(date_str)
    if not readings:
        print("⚠️ No readings found for this date.")
        return

    headers = ["id", "timestamp", "reading", "confidence", "image_path", "status", "notes"]

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(readings)

    print(f"✅ CSV exported: {output_path}")
