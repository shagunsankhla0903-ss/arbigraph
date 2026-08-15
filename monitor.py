"""
monitor.py
Runs ArbiGraph's detection loop continuously, checking for
arbitrage every 30 seconds and logging results to the database.

Stop it anytime with Ctrl+C.
"""

import time

from src.fx_fetcher import get_clean_rates
from src.graph_builder import build_graph
from src.bellman_ford import bellman_ford, cycle_profit_percent
from src.database import init_db, log_cycle, get_recent_cycles, was_recently_logged

CHECK_INTERVAL_SECONDS = 30
MIN_PROFIT_THRESHOLD = 0.05


def check_once(conn):
    """Run one full detection cycle and log the result if worthwhile."""
    rates = get_clean_rates()
    if not rates:
        print("  No rates fetched this cycle — skipping.")
        return

    graph = build_graph(rates)

    for start_currency in graph:
        cycle = bellman_ford(graph, start_currency)
        if cycle:
            profit = cycle_profit_percent(graph, cycle)
            path_str = " → ".join(cycle)

            if profit >= MIN_PROFIT_THRESHOLD:
                if was_recently_logged(conn, path_str):
                    print(f"  Arbitrage found: {path_str} ({profit:.4f}%) — already logged recently, skipping.")
                else:
                    print(f"  Arbitrage found: {path_str} ({profit:.4f}%) — logging.")
                    log_cycle(conn, cycle, profit)
            else:
                print(f"  Cycle below threshold ({profit:.4f}%) — not logged.")
            return

    print("  No arbitrage detected this cycle.")


def run_monitor():
    conn = init_db()
    print(f"ArbiGraph monitor started. Checking every {CHECK_INTERVAL_SECONDS}s. Press Ctrl+C to stop.\n")

    try:
        while True:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Checking...")
            check_once(conn)
            time.sleep(CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nStopping monitor.")
    finally:
        conn.close()


if __name__ == "__main__":
    run_monitor()