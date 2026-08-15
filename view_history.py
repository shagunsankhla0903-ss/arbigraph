"""
view_history.py
A small utility to inspect what's been logged so far.
"""

from src.database import init_db, get_recent_cycles

conn = init_db()
rows = get_recent_cycles(conn, limit=20)

if not rows:
    print("No cycles logged yet.")
else:
    print(f"Showing last {len(rows)} logged cycles:\n")
    for timestamp, path, profit in rows:
        print(f"{timestamp} | {path} | {profit:.4f}%")

conn.close()