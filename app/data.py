
import pandas as pd

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
        try:
            price = float(t.get("price", t.get("p")))
            qty = float(t.get("qty", t.get("quantity", t.get("q"))))
            ts = int(float(t.get("time", t.get("timestamp", t.get("T", t.get("E"))))))
            if price > 0 and qty > 0:
                out.append({"time": ts, "price": price, "qty": qty})
        except Exception:
            pass
    return out

def trades_to_candles(raw, rule="1min"):
    trades = normalize_trades(raw)
    if not trades:
        return pd.DataFrame(columns=["open","high","low","close","volume"])
    df = pd.DataFrame(trades)
    df["dt"] = pd.to_datetime(df["time"], unit="ms", utc=True)
    df = df.sort_values("dt").set_index("dt")
    return df.resample(rule).agg(
        open=("price","first"),
        high=("price","max"),
        low=("price","min"),
        close=("price","last"),
        volume=("qty","sum")
    ).dropna()

def normalize_ohlcv_csv(content: bytes):
    from io import BytesIO
    df = pd.read_csv(BytesIO(content))
    cols = {str(c).strip().lower(): c for c in df.columns}
    def pick(*names):
        for n in names:
            if n in cols:
                return cols[n]
        return None
    ts = pick("timestamp","time","datetime","date")
    o, h, l, c, v = [pick(x) for x in ("open","high","low","close","volume")]
    if not all([o,h,l,c]):
        raise ValueError("CSV باید ستون‌های Open, High, Low, Close و ترجیحاً Volume داشته باشد.")
    out = pd.DataFrame({
        "open": pd.to_numeric(df[o], errors="coerce"),
        "high": pd.to_numeric(df[h], errors="coerce"),
        "low": pd.to_numeric(df[l], errors="coerce"),
        "close": pd.to_numeric(df[c], errors="coerce"),
        "volume": pd.to_numeric(df[v], errors="coerce") if v else 0.0,
    })
    if ts:
        parsed = pd.to_datetime(df[ts], errors="coerce", utc=True)
        out.index = parsed
        out = out[~out.index.isna()].sort_index()
    out = out.dropna(subset=["open","high","low","close"])
    if len(out) < 60:
        raise ValueError("حداقل ۶۰ کندل برای بک‌تست لازم است.")
    return out
