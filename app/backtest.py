from .strategy import analyze
def run(c,start=1000,fee=.001,trade_quote=50):
 if len(c)<60:return {"ok":False,"error":"At least 60 candles required"}
 cash=start;qty=0;entry=0;tr=[];peak=start;dd=0
 for i in range(55,len(c)):
  w=c.iloc[:i+1];a=analyze(w);price=float(w.close.iloc[-1])
  if a["signal"]=="BUY" and qty==0:
   spend=min(trade_quote,cash);f=spend*fee;qty=(spend-f)/price;cash-=spend;entry=price;tr.append({"side":"BUY","price":price})
  elif a["signal"]=="SELL" and qty>0:
   gross=qty*price;f=gross*fee;cash+=gross-f;tr.append({"side":"SELL","price":price,"pnl":gross-f-qty*entry});qty=0;entry=0
  eq=cash+qty*price;peak=max(peak,eq);dd=max(dd,peak-eq)
 eq=cash+qty*float(c.close.iloc[-1]);sells=[x for x in tr if x["side"]=="SELL"];wins=sum(x.get("pnl",0)>0 for x in sells)
 return {"ok":True,"starting_quote":start,"final_equity":round(eq,8),"pnl":round(eq-start,8),"return_pct":round((eq/start-1)*100,4),"trades_count":len(tr),"closed_trades":len(sells),"win_rate_pct":round(wins/len(sells)*100,2) if sells else 0,"max_drawdown":round(dd,8),"open_position":qty>0,"trades":tr}
