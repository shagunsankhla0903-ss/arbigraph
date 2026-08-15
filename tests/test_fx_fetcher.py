import sys
import os

# This lets the test file find src/fx_fetcher.py, since tests/
# is a separate folder from src/
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.fx_fetcher import validate_rates


def test_validate_removes_zero_rates():
    dirty = {"USD_EUR": 0.91, "USD_BAD": 0, "USD_NEG": -1.5}
    clean = validate_rates(dirty)
    assert "USD_EUR" in clean
    assert "USD_BAD" not in clean
    assert "USD_NEG" not in clean


def test_validate_keeps_good_rates():
    rates = {"EUR_GBP": 0.856, "GBP_JPY": 190.1}
    clean = validate_rates(rates)
    assert len(clean) == 2


def test_validate_converts_to_float():
    rates = {"USD_EUR": 1}  # deliberately an int, not a float
    clean = validate_rates(rates)
    assert isinstance(clean["USD_EUR"], float)


def test_validate_handles_empty_input():
    clean = validate_rates({})
    assert clean == {}


def test_validate_rejects_non_numeric():
    dirty = {"USD_EUR": "not a number"}
    clean = validate_rates(dirty)
    assert "USD_EUR" not in clean