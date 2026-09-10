import math

def ema(values, n):
    if not values: return None
    a=2/(n+1)
    e=values[0]
    for v in values[1:]: e=a*v+(1-a)*e
    return e

def rsi(values, n=14):
    if len(values)<n+1: return None
    gains=[]; losses=[]
    for a,b in zip(values[-n-1:-1], values[-n:]):
        d=b-a
        gains.append(max(d,0)); losses.append(max(-d,0))
    ag=sum(gains)/n; al=sum(losses)/n
    if al==0: return 100.0
    return 100-100/(1+ag/al)

def atr(c, n=14):
    if len(c)<n+1:return None
    tr=[]
    for i in range(1,len(c)):
        h,l,pc=c[i]["high"],c[i]["low"],c[i-1]["close"]
        tr.append(max(h-l,abs(h-pc),abs(l-pc)))
    return sum(tr[-n:])/n

def analyze(c):
    if len(c)<55:
        return {"signal":"HOLD","confidence":0,"reason":"داده کافی نیست","ready":False}
    closes=[x["close"] for x in c]
    vols=[x["volume"] for x in c]
    e20=ema(closes,20); e50=ema(closes,50)
    rr=rsi(closes,14); aa=atr(c,14)
    fast=ema(closes,12); slow=ema(closes,26)
    # MACD line history
    macds=[]
    for i in range(26,len(closes)+1):
        macds.append(ema(closes[:i],12)-ema(closes[:i],26))
    signal_line=ema(macds,9) if macds else None
    macd=macds[-1] if macds else None
    avgvol=sum(vols[-20:])/20 if len(vols)>=20 else 0
    vol_ok=vols[-1]>=avgvol*1.05 if avgvol else False
    score=0; reasons=[]
    if e20>e50: score+=25; reasons.append("روند صعودی EMA")
    else: score-=25; reasons.append("روند نزولی EMA")
    if rr is not None:
        if rr>52 and rr<72: score+=20; reasons.append("RSI صعودی")
        elif rr<45: score-=20; reasons.append("RSI ضعیف")
    if macd is not None and signal_line is not None:
        if macd>signal_line: score+=25; reasons.append("MACD مثبت")
        else: score-=25; reasons.append("MACD منفی")
    if vol_ok:
        score += 15 if score>0 else -15
        reasons.append("حجم تأیید می‌کند")
    if score>=55:
        sig="BUY"
    elif score<=-55:
        sig="SELL"
    else:
        sig="HOLD"
    conf=min(99, max(1, 50+abs(score)/2))
    return {
        "ready":True,"signal":sig,"confidence":round(conf,1),
        "price":closes[-1],"rsi":round(rr,2) if rr is not None else None,
        "ema20":e20,"ema50":e50,"macd":macd,"macd_signal":signal_line,
        "atr":aa,"volume":vols[-1],"volume_avg":avgvol,
        "reason":"، ".join(reasons)
    }
