
import pandas as pd

def add_indicators(c):
    x=c.copy(); x['ema20']=x.close.ewm(span=20,adjust=False).mean(); x['ema50']=x.close.ewm(span=50,adjust=False).mean()
    d=x.close.diff(); g=d.clip(lower=0).rolling(14).mean(); l=(-d.clip(upper=0)).rolling(14).mean()
    rs=g/l.replace(0,pd.NA); x['rsi']=100-100/(1+rs); x['vma']=x.volume.rolling(20).mean(); x['atr']=((x.high-x.low).combine((x.high-x.close.shift()).abs(),max)).combine((x.low-x.close.shift()).abs(),max).rolling(14).mean()
    return x

def analyze(c):
    if c is None or len(c)<55:return {'signal':'HOLD','confidence':0,'reason':'برای تحلیل حداقل ۵۵ کندل لازم است.','candles':0 if c is None else len(c)}
    x=add_indicators(c); z=x.iloc[-1]; p=float(z.close); e20=float(z.ema20); e50=float(z.ema50); r=float(z.rsi) if pd.notna(z.rsi) else 50; vr=float(z.volume/z.vma) if pd.notna(z.vma) and z.vma>0 else 1
    score=0; reasons=[]
    if e20>e50:score+=1;reasons.append('روند صعودی')
    elif e20<e50:score-=1;reasons.append('روند نزولی')
    if 52<=r<=70:score+=1;reasons.append('RSI مناسب خرید')
    elif 30<=r<=48:score-=1;reasons.append('RSI مناسب فروش')
    if vr>=1.05:score+=1 if score>=0 else -1;reasons.append('تأیید حجم')
    sig='BUY' if score>=2 else 'SELL' if score<=-2 else 'HOLD'; conf=min(95,55+12*abs(score)) if sig!='HOLD' else 50
    return {'signal':sig,'confidence':conf,'price':round(p,8),'rsi':round(r,2),'ema20':round(e20,8),'ema50':round(e50,8),'volume_ratio':round(vr,3),'candles':len(x),'reason':'، '.join(reasons) or 'شرایط قوی وجود ندارد.'}
