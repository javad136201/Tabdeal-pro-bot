
from .strategy import indicators, signal
from .data import resample_ohlcv

def run(c1,starting=1000,order_usd=50,fee=.001,min_conf=70):
    if c1 is None or len(c1)<300:return {"ok":False,"error":"برای بک‌تست حداقل ۳۰۰ کندل لازم است."}
    usd=float(starting); qty=0.; entry=0.; sl=tp=0.; fees=0.; wins=losses=closed=0; peak=starting; maxdd=0.; logs=[]
    for i in range(250,len(c1)):
        w=c1.iloc[:i+1]
        a=signal(w,min_conf)
        p=float(w.close.iloc[-1])
        if qty==0 and a.get("signal")=="BUY":
            spend=min(order_usd,usd); f=spend*fee; qty=(spend-f)/p; usd-=spend; entry=p
            sl=float(a.get("suggested_sl",p*.995)); tp=float(a.get("suggested_tp",p*1.01)); fees+=f
            logs.append({"side":"BUY","price":p,"time":str(w.index[-1])})
        elif qty:
            reason=None
            if p>=tp:reason="TAKE_PROFIT"
            elif p<=sl:reason="STOP_LOSS"
            elif a.get("signal")=="SELL":reason="SIGNAL"
            if reason:
                gross=qty*p; f=gross*fee; net=gross-f; pnl=net-qty*entry
                usd+=net; fees+=f; closed+=1; wins+=pnl>0; losses+=pnl<=0
                logs.append({"side":"SELL","price":p,"pnl":round(pnl,6),"reason":reason,"time":str(w.index[-1])})
                qty=0.;entry=0.;sl=tp=0.
        eq=usd+qty*p;peak=max(peak,eq);maxdd=max(maxdd,peak-eq)
    final=usd+qty*float(c1.close.iloc[-1])
    return {"ok":True,"starting_usd":starting,"final_usd":round(final,6),"pnl_usd":round(final-starting,6),
            "return_pct":round((final/starting-1)*100,4),"closed_trades":closed,
            "winning_trades":wins,"losing_trades":losses,"win_rate":round(wins/closed*100,2) if closed else 0,
            "max_drawdown_usd":round(maxdd,6),"fees_usd":round(fees,6),"trades":logs[-200:]}
