import pandas as pd
from app.strategies.technical import signal

def run_backtest(df, initial_cash, trade_amount, fee_rate, stop_loss, take_profit, rsi_buy, rsi_sell, min_score):
    cash=float(initial_cash); asset=0.0; entry=None; trades=[]
    for i in range(60,len(df)):
        window=df.iloc[:i+1]
        sig=signal(window,rsi_buy,rsi_sell,min_score)
        p=float(window.close.iloc[-1])
        if asset==0 and sig["signal"]=="BUY":
            spend=min(trade_amount,cash)
            if spend>0:
                fee=spend*fee_rate
                asset=(spend-fee)/p; cash-=spend
                entry=p; trades.append({"side":"BUY","price":p,"amount":spend})
        elif asset>0:
            if p<=entry*(1-stop_loss) or p>=entry*(1+take_profit) or sig["signal"]=="SELL":
                gross=asset*p; fee=gross*fee_rate
                cash+=gross-fee
                trades.append({"side":"SELL","price":p,"amount":gross})
                asset=0; entry=None
    final=cash+asset*float(df.close.iloc[-1])
    ret=(final/initial_cash-1)*100
    return {"initial":initial_cash,"final":final,"return_pct":ret,"trades":trades,"trade_count":len(trades)}
