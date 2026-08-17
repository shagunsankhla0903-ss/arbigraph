"""
app.py
The FastAPI web layer for ArbiGraph. Exposes detected
arbitrage cycles over HTTP for other programs to consume.
"""
import asyncio
from src.fx_fetcher import get_clean_rates
from src.graph_builder import build_graph
from src.bellman_ford import bellman_ford, cycle_profit_percent
from src.database import log_cycle, was_recently_logged
from fastapi import FastAPI, HTTPException, Header, Depends, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from src.database import init_db, get_recent_cycles
import os
from dotenv import load_dotenv

app = FastAPI(title="ArbiGraph API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for a learning project; restrict this in real production
    allow_methods=["GET"],
    allow_headers=["*"],
)

load_dotenv()

VALID_API_KEYS = {os.getenv("VALID_API_KEYS", "test-key-123")}

MIN_PROFIT_THRESHOLD = 0.05
CHECK_INTERVAL_SECONDS = 30

async def background_monitor():
    """Runs continuously in the background, inside the same process as the API."""
    while True:
        try:
            conn = init_db()
            rates = get_clean_rates()

            if rates:
                graph = build_graph(rates)
                for start_currency in graph:
                    cycle = bellman_ford(graph, start_currency)
                    if cycle:
                        profit = cycle_profit_percent(graph, cycle)
                        path_str = " → ".join(cycle)
                        if profit >= MIN_PROFIT_THRESHOLD and not was_recently_logged(conn, path_str):
                            log_cycle(conn, cycle, profit)
                            print(f"[background] Logged: {path_str} ({profit:.4f}%)")
                        break

            conn.close()
        except Exception as e:
            print(f"[background] Error during check: {e}")

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)

@app.on_event("startup")
async def start_background_monitor():
    asyncio.create_task(background_monitor())



def check_api_key(x_api_key: str = Header(None)):
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/")


def root():
    return {"message": "ArbiGraph API is running."}


@app.get("/v1/cycles")
def get_cycles(_: None = Depends(check_api_key)):
    conn = init_db()
    rows = get_recent_cycles(conn, limit=20)
    conn.close()

    cycles = []
    for timestamp, path, profit_pct in rows:
        cycles.append({
            "timestamp": timestamp,
            "path": path,
            "profit_pct": profit_pct
        })

    return {"cycles": cycles}


@app.websocket("/v1/stream")
async def stream_cycles(websocket: WebSocket):
    await websocket.accept()
    last_sent_id = None

    try:
        while True:
            conn = init_db()
            rows = get_recent_cycles(conn, limit=1)
            conn.close()

            if rows:
                timestamp, path, profit_pct = rows[0]
                if timestamp != last_sent_id:
                    last_sent_id = timestamp
                    await websocket.send_json({
                        "timestamp": timestamp,
                        "path": path,
                        "profit_pct": profit_pct
                    })

            await asyncio.sleep(5)
    except Exception:
        await websocket.close()