"""
database.py
Handles storing and retrieving detected arbitrage cycles
using SQLite — a database that lives in a single local file.
"""

import sqlite3
from datetime import datetime, timezone

DB_FILE = "arbigraph.db"


def init_db():
    """
    Connect to the database file (creating it if it doesn't exist yet)
    and make sure the cycles table exists.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cycles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            path TEXT,
            profit_pct REAL
        )
    """)
    conn.commit()
    return conn

# if __name__ == "__main__":
#     conn = init_db()
#     print(f"Database initialized: {DB_FILE}")
#     conn.close()

def log_cycle(conn, path, profit_pct):
    """
    Save one detected cycle to the database.
    `path` should be a list of currencies, e.g. ["USD", "EUR", "GBP", "USD"]
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    path_str = " → ".join(path)

    conn.execute(
        "INSERT INTO cycles (timestamp, path, profit_pct) VALUES (?, ?, ?)",
        (timestamp, path_str, profit_pct)
    )
    conn.commit()

# if __name__ == "__main__":
#     conn = init_db()
#     print(f"Database initialized: {DB_FILE}")

#     # Log a fake test cycle
#     log_cycle(conn, ["USD", "EUR", "GBP", "USD"], 0.34)
#     print("Test cycle logged.")

#     conn.close()

def get_recent_cycles(conn, limit=10):
    """
    Return the most recently logged cycles, newest first.
    """
    cursor = conn.execute(
        "SELECT timestamp, path, profit_pct FROM cycles ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    )
    return cursor.fetchall()
def was_recently_logged(conn, path_str, within_minutes=5):
    """
    Check if this exact cycle was already logged within the last
    few minutes, to avoid spamming duplicate entries.
    """
    cursor = conn.execute(
        """
        SELECT COUNT(*) FROM cycles
        WHERE path = ?
        AND timestamp >= datetime('now', ?)
        """,
        (path_str, f"-{within_minutes} minutes")
    )
    count = cursor.fetchone()[0]
    return count > 0

if __name__ == "__main__":
    conn = init_db()

    log_cycle(conn, ["USD", "EUR", "GBP", "USD"], 0.34)
    print("Test cycle logged.\n")

    print("Recent cycles:")
    for row in get_recent_cycles(conn):
        timestamp, path, profit = row
        print(f"  {timestamp} | {path} | {profit:.4f}%")

    conn.close()

def was_recently_logged(conn, path_str, within_minutes=5):
    """
    Check if this exact cycle was already logged within the last
    few minutes, to avoid spamming duplicate entries.
    """
    cursor = conn.execute(
        """
        SELECT COUNT(*) FROM cycles
        WHERE path = ?
        AND timestamp >= datetime('now', ?)
        """,
        (path_str, f"-{within_minutes} minutes")
    )
    count = cursor.fetchone()[0]
    return count > 0