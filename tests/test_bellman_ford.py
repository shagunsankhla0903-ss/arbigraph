import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from graph_builder import build_graph
from bellman_ford import bellman_ford


def test_detects_known_arbitrage():
    rates = {"USD_EUR": 0.90, "EUR_GBP": 0.85, "GBP_USD": 1.35}
    graph = build_graph(rates)
    result = bellman_ford(graph, source="USD")
    assert result is not None
    assert "USD" in result
    assert "EUR" in result
    assert "GBP" in result


def test_no_false_positive_on_fair_rates():
    # These rates multiply to exactly 1.0 — no profit, no arbitrage
    rates = {"USD_EUR": 0.90, "EUR_GBP": 0.90, "GBP_USD": 1.2345679}
    graph = build_graph(rates)
    result = bellman_ford(graph, source="USD")
    assert result is None


def test_graph_builder_produces_correct_structure():
    rates = {"USD_EUR": 0.90}
    graph = build_graph(rates)
    assert "USD" in graph
    assert graph["USD"][0][0] == "EUR"