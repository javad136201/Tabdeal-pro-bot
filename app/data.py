import pandas as pd

def normalize_trades(raw):
    if isinstance(raw,dict):
        for k in ('data','results','trades'):
            if isinstance(raw.get(k),list): raw=raw[k]; break
        else: raw=[raw]
    out=[]
    for t in raw if isinstance(raw,list) else []:
        if not isinstance(t,dict): continue
        try:
            pv=t.get('price',t.get('p')); qv=t.get('qty',t.get('quantity',t.get('q')))
            tv=t.get('time',t.get('timestamp',t.get('T',t.get('E'))))
            p=float(pv); q=float(qv); ts=float(tv)
            if ts < 10_000_000_000: ts *= 1000
            if p>0 and q>0 and ts>0: out.append({'time':int(ts),'price':p,'qty':q})
        except Exception: continue
    return out

def trades_to_1m(raw):
    x=normalize_trades(raw)
    if not x:return pd.DataFrame(columns=['open','high','low','close','volume'])
    d=pd.DataFrame(x);d['dt']=pd.to_datetime(d.time,unit='ms',utc=True);d=d.sort_values('dt').set_index('dt')
    return d.resample('1min').agg(open=('price','first'),high=('price','max'),low=('price','min'),close=('price','last'),volume=('qty','sum')).dropna()

def csv_ohlcv(content):
    from io import BytesIO
    df=pd.read_csv(BytesIO(content)); m={str(c).strip().lower():c for c in df.columns}
    def col(*xs):
        for x in xs:
            if x in m:return m[x]
        return None
    o,h,l,c=col('open'),col('high'),col('low'),col('close');v=col('volume')
    if not all((o,h,l,c)): raise ValueError('CSV must contain Open, High, Low, Close')
    out=pd.DataFrame({'open':pd.to_numeric(df[o],errors='coerce'),'high':pd.to_numeric(df[h],errors='coerce'),'low':pd.to_numeric(df[l],errors='coerce'),'close':pd.to_numeric(df[c],errors='coerce'),'volume':pd.to_numeric(df[v],errors='coerce') if v else 0.0})
    ts=col('timestamp','time','datetime','date')
    if ts:
        raw=df[ts]
        idx=pd.to_datetime(raw,errors='coerce',utc=True)
        if idx.notna().mean()<0.5:
            idx=pd.to_datetime(pd.to_numeric(raw,errors='coerce'),unit='ms',errors='coerce',utc=True)
        out.index=idx; out=out[~out.index.isna()].sort_index()
    out=out.replace([float('inf'),float('-inf')],pd.NA).dropna()
    if len(out)<100: raise ValueError('At least 100 candles are required')
    return out

def resample(c,rule):
    if c is None or c.empty:return pd.DataFrame(columns=['open','high','low','close','volume'])
    return c.resample(rule).agg(open=('open','first'),high=('high','max'),low=('low','min'),close=('close','last'),volume=('volume','sum')).dropna()
