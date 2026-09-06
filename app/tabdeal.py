import requests

BASE = "https://api1.tabdeal.org"

def _symbol_variants(symbol: str):
    s = symbol.replace("_", "").upper()
    return [symbol.upper(), s]

def recent_trades(symbol: str, limit: int = 500):
    last_error = None
    for sym in _symbol_variants(symbol):
        try:
            r = requests.get(
                f"{BASE}/r/api/v1/trades",
                params={"symbol": sym, "limit": limit},
                timeout=10,
            )
            r.raise_for_status()
            payload = r.json()
            if isinstance(payload, list):
                return payload
            if isinstance(payload, dict):
                for key in ("data", "results", "trades"):
                    if isinstance(payload.get(key), list):
                        return payload[key]
                return [payload]
        except Exception as e:
            last_error = e
    raise RuntimeError(f"Tabdeal trades request failed: {last_error}")

def ping():
    r = requests.get(f"{BASE}/r/api/v1/ping", timeout=10)
    r.raise_for_status()
    return r.json()
