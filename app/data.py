import pandas as pd
def normalize_trades(raw):
    if isinstance(raw,dict):
        for k in ('data','results','trades'):
            if isinstance(raw.get(k),list):raw=raw[k];break
        else:raw=[raw]
    out=[]
    for t in raw if isinstance(raw,list) else []:
        if not isinstance(t,dict):continue
        try:
            p=float(t.get('price',t.get('p')));q=float(t.get('qty',t.get('quantity',t.get('q'))));ts=int(float(t.get('time',t.get('timestamp',t.get('T',t.get('E'))))))
            if p>0 and q>0:out.append({'time':ts,'price':p,'qty':q})
        except Exception:pass
    return out
def trades_to_1m(raw):
    x=normalize_trades(raw)
    if not x:return pd.DataFrame(columns=['open','high','low','close','volume'])
    d=pd.DataFrame(x);d['dt']=pd.to_datetime(d.time,unit='ms',utc=True);d=d.sort_values('dt').set_index('dt')
    return d.resample('1min').agg(open=('price','first'),high=('price','max'),low=('price','min'),close=('price','last'),volume=('qty','sum')).dropna()
def csv_ohlcv(content):
    from io import BytesIO
    df=pd.read_csv(BytesIO(content));m={str(c).strip().lower():c for c in df.columns}
    def p(*xs):
        for x in xs:
            if x in m:return m[x]
    o,h,l,c=map(p,('open',),('high',),('low',),('close',));v=p('volume')
    if not all((o,h,l,c)):raise ValueError('CSV must contain Open, High, Low, Close')
    out=pd.DataFrame({'open':pd.to_numeric(df[o],errors='coerce'),'high':pd.to_numeric(df[h],errors='coerce'),'low':pd.to_numeric(df[l],errors='coerce'),'close':pd.to_numeric(df[c],errors='coerce'),'volume':pd.to_numeric(df[v],errors='coerce') if v else 0.0})
    ts=p('timestamp','time','datetime','date')
    if ts:
        idx=pd.to_datetime(df[ts],errors='coerce',utc=True)
        if idx.isna().mean()>0.5:idx=pd.to_datetime(pd.to_numeric(df[ts],errors='coerce'),unit='ms',errors='coerce',utc=True)
        out.index=idx;out=out[~out.index.isna()].sort_index()
    if len(out)<300:raise ValueError('At least 300 candles are required')
    return out.dropna()
def resample(c,rule):
    return c.resample(rule).agg(open=('open','first'),high=('high','max'),low=('low','min'),close=('close','last'),volume=('volume','sum')).dropna()
