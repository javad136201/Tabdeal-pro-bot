import pandas as pd
def trades_to_candles(trades):
    rows=[]
    for t in trades:
        rows.append({'time':pd.to_datetime(t.get('time') or t.get('T'),unit='ms'),'price':float(t.get('price') or t.get('p')),'volume':float(t.get('qty') or t.get('q') or 0)})
    if not rows:return pd.DataFrame()
    d=pd.DataFrame(rows).set_index('time')
    c=d.price.resample('1min').ohlc(); c['volume']=d.volume.resample('1min').sum(); return c.dropna()
