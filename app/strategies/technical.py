import pandas as pd

def indicators(df):
    c=df["close"]
    ema20=c.ewm(span=20,adjust=False).mean()
    ema50=c.ewm(span=50,adjust=False).mean()
    d=c.diff()
    gain=d.clip(lower=0).ewm(alpha=1/14,adjust=False).mean()
    loss=(-d.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean()
    rs=gain/loss.replace(0,float("nan"))
    rsi=100-(100/(1+rs))
    macd=c.ewm(span=12,adjust=False).mean()-c.ewm(span=26,adjust=False).mean()
    signal=macd.ewm(span=9,adjust=False).mean()
    vol=df["volume"].rolling(20).mean()
    return ema20,ema50,rsi,macd,signal,vol

def signal(df, rsi_buy=55, rsi_sell=45, min_score=4):
    if len(df)<60: return {"signal":"WAIT","score":0,"values":{}}
    ema20,ema50,rsi,macd,ms,vol=indicators(df)
    b=s=0
    if ema20.iloc[-1]>ema50.iloc[-1]: b+=1
    if ema20.iloc[-1]<ema50.iloc[-1]: s+=1
    if rsi.iloc[-1]>=rsi_buy: b+=1
    if rsi.iloc[-1]<=rsi_sell: s+=1
    if macd.iloc[-1]>ms.iloc[-1]: b+=1
    if macd.iloc[-1]<ms.iloc[-1]: s+=1
    if df.close.iloc[-1]>ema20.iloc[-1]: b+=1
    if df.close.iloc[-1]<ema20.iloc[-1]: s+=1
    if vol.iloc[-1]>0 and df.volume.iloc[-1]>vol.iloc[-1]:
        (b if b>=s else s)
        if b>=s: b+=1
        else: s+=1
    sig="BUY" if b>=min_score and b>s else "SELL" if s>=min_score and s>b else "HOLD"
    return {"signal":sig,"score":max(b,s),"values":{
        "price":float(df.close.iloc[-1]),"rsi":float(rsi.iloc[-1]),
        "ema20":float(ema20.iloc[-1]),"ema50":float(ema50.iloc[-1]),
        "macd":float(macd.iloc[-1]),"macd_signal":float(ms.iloc[-1])
    }}
