"""
app.py
The FastAPI web layer for ArbiGraph. Exposes detected
arbitrage cycles over HTTP for other programs to consume.
"""

from fastapi import FastAPI, HTTPException, Header, Depends, WebSocket
from src.database import init_db, get_recent_cycles
import asyncio

app = FastAPI(title="ArbiGraph API")
VALID_API_KEYS = {"test-key-123"}  # replace with real key storage later


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