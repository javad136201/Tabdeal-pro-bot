import pandas as pd
from .data import resample
PROFILES={'CONSERVATIVE':(7,75),'BALANCED':(6,65),'ACTIVE':(5,55)}
def ind(c):
    x=c.copy();x['ema20']=x.close.ewm(span=20,adjust=False).mean();x['ema50']=x.close.ewm(span=50,adjust=False).mean();x['ema100']=x.close.ewm(span=100,adjust=False).mean()
    d=x.close.diff();g=d.clip(lower=0).ewm(alpha=1/14,adjust=False).mean();loss=(-d.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean();x['rsi']=100-(100/(1+g/loss.replace(0,pd.NA)))
    e12=x.close.ewm(span=12,adjust=False).mean();e26=x.close.ewm(span=26,adjust=False).mean();x['macd']=e12-e26;x['macd_sig']=x.macd.ewm(span=9,adjust=False).mean();x['macd_hist']=x.macd-x.macd_sig
    prev=x.close.shift(1);tr=pd.concat([x.high-x.low,(x.high-prev).abs(),(x.low-prev).abs()],axis=1).max(axis=1);x['atr']=tr.ewm(span=14,adjust=False).mean();x['vr']=x.volume/x.volume.rolling(20).mean();return x
def analyze(c,profile='BALANCED',min_conf=None):
    need,default=PROFILES.get(profile,PROFILES['BALANCED']);min_conf=default if min_conf is None else min_conf
    if len(c)<220:return {'ready':False,'signal':'HOLD','confidence':0,'reason':'نیاز به حداقل ۲۲۰ کندل ۱ دقیقه‌ای'}
    c5,c15=resample(c,'5min'),resample(c,'15min')
    if len(c5)<60 or len(c15)<30:return {'ready':False,'signal':'HOLD','confidence':0,'reason':'تاریخچه کافی برای تایم‌فریم‌های بالاتر نیست'}
    a1,a5,a15=ind(c),ind(c5),ind(c15);x=a1.iloc[-1];p5=a5.iloc[-1];p15=a15.iloc[-1];prev=a1.iloc[-2]
    bull=bear=0;r=[];price=float(x.close);rsi=float(x.rsi) if pd.notna(x.rsi) else 50;vr=float(x.vr) if pd.notna(x.vr) else 1;atr=float(x.atr) if pd.notna(x.atr) else price*.003
    if p15.ema20>p15.ema50>p15.ema100:bull+=2;r.append('روند ۱۵دقیقه صعودی')
    elif p15.ema20<p15.ema50<p15.ema100:bear+=2;r.append('روند ۱۵دقیقه نزولی')
    else:r.append('روند ۱۵دقیقه خنثی')
    if p5.ema20>p5.ema50 and p5.macd_hist>0:bull+=2;r.append('ستاپ ۵دقیقه صعودی')
    elif p5.ema20<p5.ema50 and p5.macd_hist<0:bear+=2;r.append('ستاپ ۵دقیقه نزولی')
    if price>prev.high and x.close>x.open:bull+=2;r.append('شکست سقف کندل')
    elif price<prev.low and x.close<x.open:bear+=2;r.append('شکست کف کندل')
    if 52<=rsi<=68:bull+=1;r.append('RSI خرید')
    elif 32<=rsi<=48:bear+=1;r.append('RSI فروش')
    if vr>=1.15:(bull:=bull+1) if bull>=bear else (bear:=bear+1);r.append('تأیید حجم')
    ext=abs(price-float(x.ema20))/atr if atr else 0
    if ext>2.5:r.append('فاصله از EMA20 زیاد است');bull=max(0,bull-1);bear=max(0,bear-1)
    score=bull-bear;conf=min(95,50+abs(score)*8+(10 if max(bull,bear)>=5 else 0));sig='BUY' if bull>=need and score>=4 else 'SELL' if bear>=need and score<=-4 else 'HOLD'
    if sig!='HOLD' and conf<min_conf:sig='HOLD';r.append('اعتماد کمتر از حد مجاز')
    sd=max(atr*1.5,price*.0025);return {'ready':True,'signal':sig,'confidence':int(conf),'price':price,'rsi':round(rsi,2),'ema20':float(x.ema20),'ema50':float(x.ema50),'ema100':float(x.ema100),'macd_hist':float(x.macd_hist),'atr':atr,'volume_ratio':vr,'trend':'BULLISH' if bull>bear else 'BEARISH' if bear>bull else 'NEUTRAL','bull_score':bull,'bear_score':bear,'suggested_sl':price-sd,'suggested_tp':price+sd*2,'reason':'، '.join(r),'candle_time':str(c.index[-1])}
