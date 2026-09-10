from collections import defaultdict
from datetime import datetime, timezone

def normalize_trades(raw):
    out=[]
    for x in raw:
        try:
            p=float(x.get("price", x.get("p")))
            q=float(x.get("qty", x.get("quantity", x.get("q", 0))))
            ts=float(x.get("time", x.get("timestamp", x.get("T", x.get("E", 0)))))
            if p > 0 and ts > 0:
                out.append({"price":p,"qty":q,"time":ts})
        except Exception:
            continue
    return sorted(out, key=lambda x:x["time"])

def candles(trades, bucket_ms=60000):
    groups=defaultdict(list)
    for t in normalize_trades(trades):
        b=int(t["time"]//bucket_ms)*bucket_ms
        groups[b].append(t)
    out=[]
    for b, rows in sorted(groups.items()):
        prices=[x["price"] for x in rows]
        out.append({
            "time": b/1000,
            "open": prices[0],
            "high": max(prices),
            "low": min(prices),
            "close": prices[-1],
            "volume": sum(x["qty"] for x in rows)
        })
    return out
