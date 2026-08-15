import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import sqlite3
from database import log_cycle, get_recent_cycles


def test_log_and_retrieve_cycle():
    # Use an in-memory database so tests never touch your real arbigraph.db
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE cycles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            path TEXT,
            profit_pct REAL
        )
    """)

    log_cycle(conn, ["USD", "EUR", "USD"], 0.12)
    rows = get_recent_cycles(conn, limit=5)

    assert len(rows) == 1
    assert rows[0][1] == "USD → EUR → USD"
    assert rows[0][2] == 0.12


def test_get_recent_cycles_respects_limit():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE cycles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            path TEXT,
            profit_pct REAL
        )
    """)

    for i in range(5):
        log_cycle(conn, ["USD", "EUR", "USD"], i * 0.1)

    rows = get_recent_cycles(conn, limit=3)
    assert len(rows) == 3