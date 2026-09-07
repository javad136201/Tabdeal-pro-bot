import pandas as pd
def normalize_trades(raw):
    if isinstance(raw,dict):
        for k in ("data","results","trades"):
            if isinstance(raw.get(k),list): raw=raw[k]; break
        else: raw=[raw]
    if not isinstance(raw,list): return []
    out=[]
    for t in raw:
        if not isinstance(t,dict): continue
        try:
            p=float(t.get("price",t.get("p"))); q=float(t.get("qty",t.get("quantity",t.get("q"))))
            ts=int(float(t.get("time",t.get("timestamp",t.get("T",t.get("E"))))))
            if p>0 and q>0: out.append({"time":ts,"price":p,"qty":q})
        except Exception: pass
    return out
def trades_to_candles(raw):
    x=normalize_trades(raw)
    if not x: return pd.DataFrame(columns=["open","high","low","close","volume"])
    d=pd.DataFrame(x); d["dt"]=pd.to_datetime(d.time,unit="ms",utc=True); d=d.set_index("dt")
    return d.resample("1min").agg(open=("price","first"),high=("price","max"),low=("price","min"),close=("price","last"),volume=("qty","sum")).dropna()
