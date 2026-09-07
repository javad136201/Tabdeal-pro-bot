
import requests

BASE = "https://api1.tabdeal.org"

def recent_trades(symbol: str, limit: int = 800):
    last_error = None
    for s in (symbol.upper(), symbol.replace("_", "").upper()):
        try:
            r = requests.get(
                f"{BASE}/r/api/v1/trades",
                params={"symbol": s, "limit": limit},
                timeout=12,
            )
            r.raise_for_status()
            payload = r.json()
            if isinstance(payload, list):
                return payload
            if isinstance(payload, dict):
                for k in ("data", "results", "trades"):
                    if isinstance(payload.get(k), list):
                        return payload[k]
                return [payload]
        except Exception as e:
            last_error = e
    raise RuntimeError(f"Tabdeal market request failed: {last_error}")
