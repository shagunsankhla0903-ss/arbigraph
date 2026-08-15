"""
main.py
Full ArbiGraph pipeline: fetch rates, build the graph,
and check for arbitrage using Bellman-Ford.
"""

from src.fx_fetcher import get_clean_rates
from src.graph_builder import build_graph
from src.bellman_ford import bellman_ford ,cycle_profit_percent
from src.database import init_db, log_cycle

import math

MIN_PROFIT_THRESHOLD = 0.05  # percent

def cycle_profit_percent(graph, cycle):
    """Calculate the real % profit for a detected cycle."""
    total_log_weight = 0
    for i in range(len(cycle) - 1):
        base, target = cycle[i], cycle[i + 1]
        for t, w in graph[base]:
            if t == target:
                total_log_weight += w
                break
    profit = math.exp(-total_log_weight) - 1
    return profit * 100


def main():
    conn = init_db()

    print("Fetching live currency rates...")
    rates = get_clean_rates()

    if not rates:
        print("No rates were fetched. Check your internet connection.")
        conn.close()
        return

    print(f"Fetched {len(rates)} valid pairs.\n")
    graph = build_graph(rates)

    MIN_PROFIT_THRESHOLD = 0.05

    for start_currency in graph:
        cycle = bellman_ford(graph, start_currency)
        if cycle:
            profit = cycle_profit_percent(graph, cycle)
            if profit >= MIN_PROFIT_THRESHOLD:
                print(f"Arbitrage opportunity found: {' → '.join(cycle)}")
                print(f"Estimated profit: {profit:.4f}%")
                log_cycle(conn, cycle, profit)
                print("Logged to database.")
            else:
                print(f"Cycle found but below threshold ({profit:.4f}%) — not logged.")
            conn.close()
            return

    print("No arbitrage opportunity detected right now.")
    conn.close()


if __name__ == "__main__":
    main()
