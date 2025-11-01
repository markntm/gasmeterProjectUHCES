import sqlite3
from secret import *

def initialize_database(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create reading table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        reading TEXT,
        location TEXT,
        confidence REAL,
        image_path TEXT,
        status TEXT DEFAULT 'success',
        notes TEXT
    )
    """)

    # Create settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # Initialize default settings if not present
    cursor.execute("""
    INSERT OR IGNORE INTO settings (key, value)
    VALUES ('interval_minutes', '30')
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized at", db_path)

if __name__ == "__main__":
    initialize_database()
