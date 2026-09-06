import pandas as pd
def normalize_trades(raw):
    if isinstance(raw,dict):
        for k in ("data","results","trades"):
            if isinstance(raw.get(k),list): raw=raw[k]; break
        else: raw=[raw]
    if not isinstance(raw,(list,tuple)): return []
    out=[]
    for x in raw:
        if not isinstance(x,dict): continue
        p=x.get("price",x.get("p")); q=x.get("qty",x.get("quantity",x.get("q",0)))
        t=x.get("time",x.get("timestamp",x.get("T",x.get("E"))))
        if p is None or t is None: continue
        try: out.append({"time":int(float(t)),"price":float(p),"qty":float(q or 0)})
        except: pass
    return out
def trades_to_candles(raw):
    t=normalize_trades(raw)
    if not t: return pd.DataFrame()
    df=pd.DataFrame(t); df["time"]=pd.to_datetime(df["time"],unit="ms",utc=True)
    df=df.sort_values("time").set_index("time")
    c=df["price"].resample("1min").ohlc(); c["volume"]=df["qty"].resample("1min").sum()
    return c.dropna(subset=["open","high","low","close"]).reset_index()
