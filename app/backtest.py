from .strategy import analyze

def run(candles, balance=1000, trade_usd=50, fee_pct=0.1, tp_pct=1.0, sl_pct=0.6):
    cash=balance; pos=None; trades=[]
    for i in range(55,len(candles)):
        hist=candles[:i+1]; a=analyze(hist); p=hist[-1]["close"]
        if pos:
            if p>=pos["tp"] or p<=pos["sl"]:
                gross=(p-pos["entry"])*pos["qty"]
                fee=p*pos["qty"]*fee_pct/100
                pnl=gross-pos["fee"]-fee
                cash+=gross-fee
                trades.append({"entry":pos["entry"],"exit":p,"pnl":round(pnl,4),"reason":"TP" if p>=pos["tp"] else "SL"})
                pos=None
        if not pos and a.get("signal")=="BUY" and a.get("confidence",0)>=65 and cash>=trade_usd:
            qty=trade_usd/p; fee=trade_usd*fee_pct/100; cash-=fee
            pos={"entry":p,"qty":qty,"fee":fee,"tp":p*(1+tp_pct/100),"sl":p*(1-sl_pct/100)}
    if pos:
        p=candles[-1]["close"]; gross=(p-pos["entry"])*pos["qty"]; fee=p*pos["qty"]*fee_pct/100
        cash+=gross-fee
        trades.append({"entry":pos["entry"],"exit":p,"pnl":round(gross-pos["fee"]-fee,4),"reason":"END"})
    pnl=cash-balance
    wins=sum(1 for x in trades if x["pnl"]>0)
    return {"ok":True,"starting_balance":balance,"final_balance":round(cash,4),
            "pnl_usd":round(pnl,4),"return_pct":round(pnl/balance*100,3),
            "trades_count":len(trades),"win_rate":round(wins/len(trades)*100,2) if trades else 0,
            "trades":trades[-100:]}
