
import math
import pandas as pd
from .data import resample_ohlcv

def indicators(c):
    x=c.copy()
    x["ema20"]=x.close.ewm(span=20,adjust=False).mean()
    x["ema50"]=x.close.ewm(span=50,adjust=False).mean()
    x["ema100"]=x.close.ewm(span=100,adjust=False).mean()
    d=x.close.diff()
    gain=d.clip(lower=0).ewm(alpha=1/14,adjust=False).mean()
    loss=(-d.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean()
    rs=gain/loss.replace(0,pd.NA)
    x["rsi"]=100-(100/(1+rs))
    e12=x.close.ewm(span=12,adjust=False).mean()
    e26=x.close.ewm(span=26,adjust=False).mean()
    x["macd"]=e12-e26
    x["macd_signal"]=x.macd.ewm(span=9,adjust=False).mean()
    x["macd_hist"]=x.macd-x.macd_signal
    pc=x.close.shift(1)
    tr=pd.concat([(x.high-x.low),(x.high-pc).abs(),(x.low-pc).abs()],axis=1).max(axis=1)
    x["atr"]=tr.ewm(span=14,adjust=False).mean()
    x["vol_ma20"]=x.volume.rolling(20).mean()
    x["vol_ratio"]=x.volume/x.vol_ma20
    x["range"]=x.high-x.low
    return x

def signal(c1, min_conf=70):
    if c1 is None or len(c1)<220:
        return {"signal":"HOLD","confidence":0,"ready":False,"reason":"برای استراتژی چندلایه حداقل ۲۲۰ کندل ۱ دقیقه‌ای لازم است."}
    c5=resample_ohlcv(c1,"5min")
    c15=resample_ohlcv(c1,"15min")
    if len(c5)<80 or len(c15)<40:
        return {"signal":"HOLD","confidence":0,"ready":False,"reason":"برای تأیید چند تایم‌فریم، تاریخچه بیشتری لازم است.","candles_1m":len(c1),"candles_5m":len(c5),"candles_15m":len(c15)}
    a1=indicators(c1); a5=indicators(c5); a15=indicators(c15)
    x=a1.iloc[-1]; p5=a5.iloc[-1]; p15=a15.iloc[-1]
    prev=a1.iloc[-2]
    price=float(x.close); atr=float(x.atr) if pd.notna(x.atr) else 0
    rsi=float(x.rsi) if pd.notna(x.rsi) else 50
    vr=float(x.vol_ratio) if pd.notna(x.vol_ratio) else 1
    bull=0; bear=0; reasons=[]
    # 15m regime
    if p15.ema20>p15.ema50 and p15.ema50>p15.ema100:
        bull+=2; reasons.append("روند ۱۵دقیقه صعودی")
    elif p15.ema20<p15.ema50 and p15.ema50<p15.ema100:
        bear+=2; reasons.append("روند ۱۵دقیقه نزولی")
    else:
        reasons.append("روند ۱۵دقیقه خنثی؛ ورود سخت‌گیرانه شد")
    # 5m setup
    if p5.ema20>p5.ema50 and p5.macd_hist>0:
        bull+=2; reasons.append("ستاپ ۵دقیقه صعودی")
    elif p5.ema20<p5.ema50 and p5.macd_hist<0:
        bear+=2; reasons.append("ستاپ ۵دقیقه نزولی")
    # 1m trigger
    if price>float(prev.high) and x.close>x.open:
        bull+=2; reasons.append("شکست سقف کندل قبلی")
    elif price<float(prev.low) and x.close<x.open:
        bear+=2; reasons.append("شکست کف کندل قبلی")
    if 52<=rsi<=68:
        bull+=1; reasons.append("RSI مومنتوم خرید")
    elif 32<=rsi<=48:
        bear+=1; reasons.append("RSI مومنتوم فروش")
    if vr>=1.15:
        if bull>=bear: bull+=1
        else: bear+=1
        reasons.append("حجم تأییدکننده")
    extension=abs(price-float(x.ema20))/atr if atr>0 else 0
    if extension>2.2:
        bull=max(0,bull-1); bear=max(0,bear-1); reasons.append("حرکت نسبت به ATR بیش‌ازحد شده")
    score=bull-bear
    confidence=min(95,50+abs(score)*8+10*int(max(bull,bear)>=4))
    sig="BUY" if bull>=6 and score>=4 else "SELL" if bear>=6 and score<=-4 else "HOLD"
    if sig!="HOLD" and confidence<min_conf:
        sig="HOLD"; reasons.append("اعتماد به حداقل تعیین‌شده نرسیده")
    trend="BULLISH" if bull>bear else "BEARISH" if bear>bull else "NEUTRAL"
    stop_dist=max(atr*1.5,price*0.0025)
    tp_dist=stop_dist*2
    return {"signal":sig,"confidence":int(confidence),"ready":True,"price":round(price,8),
            "rsi":round(rsi,2),"ema20":round(float(x.ema20),8),"ema50":round(float(x.ema50),8),
            "ema100":round(float(x.ema100),8),"macd_hist":round(float(x.macd_hist),8),
            "atr":round(atr,8),"volume_ratio":round(vr,3),"extension_atr":round(extension,3),
            "trend":trend,"bull_score":bull,"bear_score":bear,
            "stop_distance":round(stop_dist,8),"tp_distance":round(tp_dist,8),
            "suggested_sl":round(price-stop_dist,8),"suggested_tp":round(price+tp_dist,8),
            "reason":"، ".join(reasons),"candles_1m":len(c1),"candles_5m":len(c5),"candles_15m":len(c15),
            "candle_time":str(c1.index[-1])}
