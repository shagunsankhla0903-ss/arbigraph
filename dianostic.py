import os
import sys
import subprocess
import requests

def check_environment():
    env_active = sys.prefix.endswith("venv")
    print("Environment:", "OK" if env_active else "Not active")

def check_python_path():
    print("Python path:", sys.executable)

def check_packages():
    try:
        import requests
        print("Packages: requests installed")
    except ImportError:
        print("Packages: requests NOT installed")

def check_api():
    try:
        url = "https://api.frankfurter.app/latest?from=USD"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if "rates" in data and data["rates"]:
            print("API call: success")
        else:
            print("API call: empty response")
    except Exception as e:
        print("API call: failed →", e)

def check_valid_pairs():
    from src.fx_fetcher import get_clean_rates
    rates = get_clean_rates()
    print("Valid pairs:", len(rates))

def check_tests():
    try:
        result = subprocess.run(["pytest", "tests", "-q"], capture_output=True, text=True)
        if "failed" not in result.stdout.lower():
            print("Tests: all passed")
        else:
            print("Tests: some failed")
            print(result.stdout)
    except Exception as e:
        print("Tests: could not run →", e)

if __name__ == "__main__":
    check_environment()
    check_python_path()
    check_packages()
    check_api()
    check_valid_pairs()
    check_tests()
