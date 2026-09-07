
from .strategy import analyze

def run_backtest(candles, starting=1000, order_quote=50, fee_rate=0.001, tp_pct=1.5, sl_pct=1.0, trailing_pct=0.5, min_confidence=60):
    if candles is None or len(candles)<60:
        return {"ok":False,"error":"حداقل ۶۰ کندل لازم است."}
    cash=float(starting); qty=0.0; entry=0.0; high=0.0; fees=0.0
    wins=losses=closed=0; peak=starting; max_dd=0.0; logs=[]
    for i in range(55,len(candles)):
        w=candles.iloc[:i+1]
        a=analyze(w,min_confidence)
        p=float(w.close.iloc[-1])
        if qty==0 and a["signal"]=="BUY":
            spend=min(order_quote,cash)
            fee=spend*fee_rate
            qty=(spend-fee)/p
            cash-=spend
            entry=p; high=p; fees+=fee
            logs.append({"side":"BUY","price":p})
        elif qty>0:
            high=max(high,p)
            tp=entry*(1+tp_pct/100); sl=entry*(1-sl_pct/100); trail=high*(1-trailing_pct/100)
            reason=None
            if p>=tp: reason="TAKE_PROFIT"
            elif p<=sl: reason="STOP_LOSS"
            elif p<=trail: reason="TRAILING_STOP"
            elif a["signal"]=="SELL": reason="SIGNAL"
            if reason:
                gross=qty*p; fee=gross*fee_rate
                net=gross-fee; pnl=net-qty*entry
                cash+=net; fees+=fee; closed+=1
                wins += pnl>0; losses += pnl<=0
                logs.append({"side":"SELL","price":p,"pnl":round(pnl,6),"reason":reason})
                qty=0; entry=0; high=0
        equity=cash+qty*p
        peak=max(peak,equity); max_dd=max(max_dd,peak-equity)
    final=cash+qty*float(candles.close.iloc[-1])
    return {"ok":True,"starting":starting,"order_quote":order_quote,"final_equity":round(final,6),
            "pnl":round(final-starting,6),"return_pct":round((final/starting-1)*100,4),
            "closed_trades":closed,"winning_trades":wins,"losing_trades":losses,
            "win_rate":round(wins/closed*100,2) if closed else 0,
            "max_drawdown":round(max_dd,6),"fees":round(fees,6),"trades":logs[-100:]}
