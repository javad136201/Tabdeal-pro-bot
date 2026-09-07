from datetime import datetime, timezone
import pandas as pd

def _num(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def normalize_trades(raw):
    if isinstance(raw, dict):
        for key in ("data", "results", "trades"):
            if isinstance(raw.get(key), list):
                raw = raw[key]
                break
        else:
            raw = [raw]
    if not isinstance(raw, list):
        return []

    out = []
    for t in raw:
        if not isinstance(t, dict):
            continue
        price = _num(t.get("price", t.get("p")))
        qty = _num(t.get("qty", t.get("quantity", t.get("q"))))
        ts = t.get("time", t.get("timestamp", t.get("T", t.get("E"))))
        try:
            ts = int(float(ts))
        except Exception:
            continue
        if price > 0 and qty > 0:
            out.append({"time": ts, "price": price, "qty": qty})
    return out

def trades_to_candles(raw):
    trades = normalize_trades(raw)
    if not trades:
        return pd.DataFrame(columns=["open","high","low","close","volume"])

    df = pd.DataFrame(trades)
    df["dt"] = pd.to_datetime(df["time"], unit="ms", utc=True)
    df = df.sort_values("dt").set_index("dt")
    candles = df.resample("1min").agg(
        open=("price","first"),
        high=("price","max"),
        low=("price","min"),
        close=("price","last"),
        volume=("qty","sum"),
    ).dropna()
    return candles
