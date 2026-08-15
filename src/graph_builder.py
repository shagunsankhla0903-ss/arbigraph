"""
graph_builder.py
Converts a flat rate dictionary (from fx_fetcher.py) into a graph
structure that bellman_ford.py can search for negative cycles.
"""

import math


def build_graph(rates: dict) -> dict:
    """
    Convert {"USD_EUR": 0.9142, ...} into a graph:
    {"USD": [("EUR", 0.0896), ...], ...}

    Each edge weight is -log(rate) — this is the entire trick
    that makes arbitrage detection possible with Bellman-Ford.
    """
    graph = {}

    for pair, rate in rates.items():
        base, target = pair.split("_")
        weight = -math.log(rate)

        if base not in graph:
            graph[base] = []
        graph[base].append((target, weight))

    return graph

if __name__ == "__main__":
    test_rates = {
        "USD_EUR": 0.90,
        "EUR_GBP": 0.85,
        "GBP_USD": 1.35,
    }

    graph = build_graph(test_rates)

    for node, edges in graph.items():
        print(f"{node}:")
        for target, weight in edges:
            print(f"  → {target}  (weight: {weight:.6f})")

if __name__ == "__main__":
    from fx_fetcher import get_clean_rates

    rates = get_clean_rates()
    graph = build_graph(rates)

    print(f"Graph built with {len(graph)} currency nodes.")
    sample_node = list(graph.keys())[0]
    print(f"\nSample — edges from {sample_node}:")
    for target, weight in graph[sample_node]:
        print(f"  → {target}  (weight: {weight:.6f})")