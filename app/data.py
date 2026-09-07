
import pandas as pd

def normalize_trades(raw):
    if isinstance(raw,dict):
        for k in ('data','results','trades'):
            if isinstance(raw.get(k),list): raw=raw[k]; break
        else: raw=[raw]
    if not isinstance(raw,list): return []
    out=[]
    for t in raw:
        if not isinstance(t,dict): continue
        try:
            p=float(t.get('price',t.get('p'))); q=float(t.get('qty',t.get('quantity',t.get('q'))))
            ts=int(float(t.get('time',t.get('timestamp',t.get('T',t.get('E'))))))
            if p>0 and q>0: out.append({'time':ts,'price':p,'qty':q})
        except Exception: continue
    return out

def trades_to_candles(raw,rule='1min'):
    x=normalize_trades(raw)
    if not x:return pd.DataFrame(columns=['open','high','low','close','volume'])
    d=pd.DataFrame(x); d['dt']=pd.to_datetime(d.time,unit='ms',utc=True); d=d.sort_values('dt').set_index('dt')
    return d.resample(rule).agg(open=('price','first'),high=('price','max'),low=('price','min'),close=('price','last'),volume=('qty','sum')).dropna()

def normalize_ohlcv_csv(df):
    cols={c.lower().strip():c for c in df.columns}
    def pick(*names):
        for n in names:
            if n in cols:return cols[n]
        return None
    mapping={k:pick(k,*alts) for k,alts in {'timestamp':['time','date','datetime'],'open':[],'high':[],'low':[],'close':[],'volume':['vol']}.items()}
    req=['open','high','low','close']
    if not all(mapping[k] for k in req): raise ValueError('CSV columns must include open, high, low, close')
    out=df.rename(columns={v:k for k,v in mapping.items() if v}).copy()
    if 'timestamp' in out:
        ts=out['timestamp']
        if pd.api.types.is_numeric_dtype(ts):
            unit='ms' if float(ts.dropna().iloc[0])>1e11 else 's'
            out.index=pd.to_datetime(ts,unit=unit,utc=True)
        else: out.index=pd.to_datetime(ts,utc=True)
    else: out.index=pd.RangeIndex(len(out))
    out['volume']=out['volume'].astype(float) if 'volume' in out else 1.0
    for c in ['open','high','low','close','volume']: out[c]=pd.to_numeric(out[c],errors='coerce')
    return out[['open','high','low','close','volume']].dropna().sort_index()
