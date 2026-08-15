"""
bellman_ford.py
Implements the Bellman-Ford algorithm with negative-cycle detection.
A detected negative cycle IS a currency arbitrage opportunity.
"""

import math


def bellman_ford(graph: dict, source: str):
    """
    Run Bellman-Ford from a source node.
    Returns a cycle (list of currencies) if arbitrage is found, else None.
    """
    nodes = list(graph.keys())

    # Step 1: every node starts "infinitely far away" except the source
    dist = {node: math.inf for node in nodes}
    pred = {node: None for node in nodes}
    dist[source] = 0
    # Step 2: relax every edge, V-1 times
    for _ in range(len(nodes) - 1):
        for u in graph:
            for v, w in graph[u]:
                if dist[u] + w < dist.get(v, math.inf):
                    dist[v] = dist[u] + w
                    pred[v] = u
    # Step 3: one more pass — if anything STILL improves,
    # a negative cycle exists (arbitrage!)
    for u in graph:
        for v, w in graph[u]:
            if dist[u] + w < dist.get(v, math.inf):
                return trace_cycle(pred, v)

    return None  # no arbitrage found



def trace_cycle(pred, start):
    """
    Walk backwards through predecessors to find the actual
    sequence of currencies that forms the arbitrage loop.
    """
    visited = set()
    node = start

    # Step back until we land on a node we've already seen —
    # that confirms we're inside the cycle itself
    while node not in visited:
        visited.add(node)
        node = pred[node]

    # Now walk the cycle from that repeated node back to itself
    cycle = [node]
    curr = pred[node]
    while curr != node:
        cycle.append(curr)
        curr = pred[curr]
    cycle.append(node)
    cycle.reverse()

    return cycle
if __name__ == "__main__":
    from graph_builder import build_graph

    test_rates = {
        "USD_EUR": 0.90,
        "EUR_GBP": 0.85,
        "GBP_USD": 1.35,
    }

    graph = build_graph(test_rates)
    result = bellman_ford(graph, source="USD")

    if result:
        print(f"Arbitrage found: {' → '.join(result)}")
    else:
        print("No arbitrage detected.")

def cycle_profit_percent(graph, cycle):
    """
    Calculate the real percentage profit for a detected cycle,
    by reversing the log-transform back into an actual rate product.
    """
    total_log_weight = 0

    for i in range(len(cycle) - 1):
        base, target = cycle[i], cycle[i + 1]
        for t, w in graph[base]:
            if t == target:
                total_log_weight += w
                break

    profit = math.exp(-total_log_weight) - 1
    return profit * 100