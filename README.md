# ArbiGraph

![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)

A currency arbitrage detector that models exchange rates as a graph and uses the Bellman-Ford algorithm to find profitable trading cycles in real time.

## How it works

Currency arbitrage exists when converting through a cycle of currencies (e.g. USD → EUR → GBP → USD) results in more money than you started with.

ArbiGraph detects this by:

1. Fetching live exchange rates for multiple currencies
2. Modeling each currency as a graph node, with exchange rates as weighted edges
3. Transforming each rate using `-log(rate)` — this converts the multiplication of exchange rates into addition of edge weights, and turns a profitable cycle into a **negative-weight cycle**
4. Running the Bellman-Ford algorithm, which can detect negative cycles — exactly the signal for a real arbitrage opportunity

## Example output

```
Fetching live currency rates...
Fetched 56 valid pairs.
Checking for arbitrage opportunities...

Arbitrage opportunity found: USD → EUR → GBP → USD
Estimated profit: 0.34%
```

## Live demo

The API is deployed and publicly accessible:

```
https://arbigraph-production.up.railway.app/docs
```

## Installation

```bash
git clone https://github.com/yourusername/arbigraph.git
cd arbigraph
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your own values:

```bash
cp .env.example .env  # Windows: copy .env.example .env
```

## Usage

Run a single detection check:
```bash
python main.py
```

Run continuous monitoring (checks every 30 seconds):
```bash
python monitor.py
```

Start the API server:
```bash
uvicorn app:app --reload
```
Then visit `http://localhost:8000/docs` for interactive API documentation.

## API reference

| Endpoint | Method | Auth required | Description |
|---|---|---|---|
| `/` | GET | No | Health check |
| `/v1/cycles` | GET | Yes (`X-API-Key` header) | Latest detected arbitrage cycles |
| `/v1/stream` | WebSocket | No | Live push of new cycles as they're detected |
| `/docs` | GET | No | Interactive API documentation |

## Project structure

```
arbigraph/
├── src/
│   ├── fx_fetcher.py       # Live exchange rate fetching + validation
│   ├── graph_builder.py    # Converts rates into a weighted graph
│   ├── bellman_ford.py     # Negative-cycle detection engine
│   └── database.py         # SQLite persistence layer
├── tests/                  # Unit tests for every module
├── app.py                  # FastAPI web layer
├── main.py                 # Single-run detection entry point
├── monitor.py               # Continuous monitoring loop
├── Dockerfile
└── requirements.txt
```

## Tech stack

- **Python** — core language
- **Bellman-Ford algorithm** — negative-cycle detection for arbitrage
- **FastAPI** — REST API layer with auto-generated docs
- **SQLite** — persistent storage for detected cycles
- **Docker** — containerized for consistent deployment
- **Railway** — cloud hosting

## Testing

```bash
pytest tests/ -v
```

## Notes

While testing on live data, this project surfaced a real data-quality issue: independently-sourced inverse currency rates (e.g. CAD→NZD and NZD→CAD from separate API calls) rarely multiply to exactly 1.0, which can trigger false positive "arbitrage" detections that are actually just rounding noise. This was solved by calculating true profit percentage and filtering results below a meaningful threshold.

## License

MIT License — see [LICENSE](LICENSE) for details.
