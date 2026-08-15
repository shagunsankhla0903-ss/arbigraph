"""
fx_fetcher.py
Fetches live currency exchange rates and prepares them for the
Bellman-Ford arbitrage detector in Phase 2.
"""
import os
import time
import requests
from dotenv import load_dotenv
load_dotenv()

# The currencies we care about. Add more here later if you want
# a bigger graph — just make sure Frankfurter supports them.
CURRENCIES = [
    "AUD", "BRL", "CAD", "CHF", "CNY", "CZK", "DKK",
    "EUR", "GBP", "HKD", "HUF", "IDR", "ILS", "INR", "ISK",
    "JPY", "KRW", "MXN", "MYR", "NOK", "NZD", "PHP", "PLN",
    "RON", "SEK", "SGD", "THB", "TRY", "USD", "ZAR"
]



def fetch_rates(base="USD"):
    """
    Fetch live exchange rates for ONE base currency.

    Example:
        fetch_rates("USD") -> {"EUR": 0.9142, "GBP": 0.7823, "JPY": 149.52, ...}
    """
    url = f"https://api.frankfurter.app/latest?from={base}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()   # stops the program with a clear error if the API fails
    data = response.json()
    return data["rates"]

def fetch_from_exchangerate_api(base="USD"):
    """Fallback data source using ExchangeRate-API."""
    api_key = os.getenv("EXCHANGERATE_API_KEY")
    if not api_key:
        raise ValueError("EXCHANGERATE_API_KEY not set")

    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data["conversion_rates"]

def fetch_rates_resilient(base="USD"):
    """Try Frankfurter first; fall back to ExchangeRate-API if it fails."""
    try:
        return fetch_rates_with_retry(base)
    except Exception as e:
        print(f"  Frankfurter failed for {base}, trying fallback: {e}")
        try:
            return fetch_from_exchangerate_api(base)
        except Exception as e2:
            print(f"  Fallback also failed for {base}: {e2}")
            return {}

def fetch_rates_with_retry(base="USD", retries=3):
    """
    Same as fetch_rates(), but tries again if the network hiccups.
    Waits 1 second between attempts.
    """
    for attempt in range(retries):
        try:
            return fetch_rates(base)
        except requests.exceptions.RequestException as e:
            print(f"  [warn] attempt {attempt + 1}/{retries} for {base} failed: {e}")
            time.sleep(1)
    print(f"  [error] giving up on {base} after {retries} attempts.")
    return {}


def fetch_all_rates():
    """
    Build a FULL pair-rate dictionary across every currency in CURRENCIES.

    Example output:
        {
            "USD_EUR": 0.9142,
            "USD_GBP": 0.7823,
            "EUR_GBP": 0.8556,
            ...
        }
    """
    all_rates = {}

    for base in CURRENCIES:
        print(f"Fetching rates for {base}...")
        rates = fetch_rates_resilient(base)

        for target, rate in rates.items():
            if target in CURRENCIES:
                pair = f"{base}_{target}"
                all_rates[pair] = rate

    return all_rates


def validate_rates(rates):
    """
    Remove anything that isn't a usable positive number.

    Why this matters: Phase 2 applies -log(rate) to every value.
    log(0) and log(negative) are undefined and will crash the program,
    so we filter those out here, before they ever reach that code.
    """
    clean = {}

    for pair, rate in rates.items():
        if not isinstance(rate, (int, float)):
            print(f"  [skip] {pair}: not a number ({rate})")
            continue
        if rate <= 0:
            print(f"  [skip] {pair}: invalid value ({rate})")
            continue
        clean[pair] = float(rate)

    return clean


def get_clean_rates():
    """
    The single function everything else (main.py, graph_builder.py)
    should call. Fetches, then cleans, in one step.
    """
    raw = fetch_all_rates()
    return validate_rates(raw)


# This block only runs when you execute this file directly
# (python src/fx_fetcher.py) — not when another file imports from it.
if __name__ == "__main__":
    rates = get_clean_rates()

    print(f"\nTotal valid pairs: {len(rates)}\n")
    for pair, rate in sorted(rates.items()):
        print(f"{pair}: {rate:.6f}")
