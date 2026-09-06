import pandas as pd
def rsi(s,n=14):
    d=s.diff(); g=d.clip(lower=0); l=-d.clip(upper=0)
    ag=g.ewm(alpha=1/n,adjust=False,min_periods=n).mean()
    al=l.ewm(alpha=1/n,adjust=False,min_periods=n).mean()
    return 100-(100/(1+ag/al.replace(0,pd.NA)))
def analyze_dataframe(df):
    if df is None or len(df)<20: return {"signal":"HOLD","score":0,"confidence":0,"reason":"NOT_ENOUGH_DATA"}
    x=df.copy(); x["ema20"]=x.close.ewm(span=20,adjust=False).mean(); x["ema50"]=x.close.ewm(span=50,adjust=False).mean()
    x["rsi"]=rsi(x.close); x["vma"]=x.volume.rolling(20).mean(); z=x.iloc[-1]; score=0; reasons=[]
    if z.ema20>z.ema50: score+=1; reasons.append("EMA_UP")
    elif z.ema20<z.ema50: score-=1; reasons.append("EMA_DOWN")
    if pd.notna(z.rsi):
        if z.rsi<30: score+=1; reasons.append("RSI_OVERSOLD")
        elif z.rsi>70: score-=1; reasons.append("RSI_OVERBOUGHT")
    if pd.notna(z.vma) and z.volume>z.vma:
        score += 1 if z.close>=z.open else -1; reasons.append("VOLUME_CONFIRM")
    sig="BUY" if score>=2 else "SELL" if score<=-2 else "HOLD"
    return {"signal":sig,"score":int(score),"confidence":min(95,50+abs(score)*15),"price":float(z.close),
            "rsi":None if pd.isna(z.rsi) else round(float(z.rsi),2),"ema20":float(z.ema20),"ema50":float(z.ema50),
            "volume":float(z.volume),"reason":",".join(reasons) or "NO_CONFIRMATION","candles":len(x)}
