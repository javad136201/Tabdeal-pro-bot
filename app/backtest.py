
from .strategy import analyze

def run(candles,starting=1000.,fee_rate=.001,tp=1.5,sl=1.0):
    if candles is None or len(candles)<60:return {'ok':False,'error':'حداقل ۶۰ کندل برای بک‌تست لازم است.'}
    cash=starting;qty=0.;entry=0.;wins=losses=0;closed=0;peak=starting;maxdd=0;logs=[]
    for i in range(55,len(candles)):
        w=candles.iloc[:i+1];a=analyze(w);p=float(w.close.iloc[-1])
        if qty==0 and a['signal']=='BUY':
            fee=cash*fee_rate;qty=(cash-fee)/p;entry=p;cash=0;logs.append({'side':'BUY','price':p})
        elif qty>0:
            if p>=entry*(1+tp/100) or p<=entry*(1-sl/100) or a['signal']=='SELL':
                gross=qty*p;fee=gross*fee_rate;cash=gross-fee;pnl=cash-qty*entry;closed+=1;wins+=pnl>0;losses+=pnl<=0;logs.append({'side':'SELL','price':p,'pnl':pnl});qty=0;entry=0
        eq=cash+qty*p;peak=max(peak,eq);maxdd=max(maxdd,peak-eq)
    final=cash+qty*float(candles.close.iloc[-1])
    return {'ok':True,'starting':starting,'final_equity':round(final,6),'pnl':round(final-starting,6),'return_pct':round((final/starting-1)*100,4),'closed_trades':closed,'win_rate':round(wins/closed*100,2) if closed else 0,'max_drawdown':round(maxdd,6),'trades':logs,'open_position':bool(qty),'note':'برای نتیجه معتبر، CSV تاریخی واقعی با open/high/low/close وارد کنید.'}
