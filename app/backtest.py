from .strategy import analyze
def run(c,start=1000,order=50,fee=.001,profile='BALANCED',conf=65):
 cash=float(start);qty=0.;entry=sl=tp=0.;fees=0.;wins=losses=closed=0;peak=start;dd=0
 logs=[]
 for i in range(250,len(c)):
  w=c.iloc[:i+1];a=analyze(w,profile,conf);p=float(w.close.iloc[-1])
  if not qty and a.get('signal')=='BUY':
   spend=min(order,cash);f=spend*fee;qty=(spend-f)/p;cash-=spend;entry=p;sl=float(a['suggested_sl']);tp=float(a['suggested_tp']);fees+=f;logs.append({'side':'BUY','price':p})
  elif qty:
   reason='TAKE_PROFIT' if p>=tp else 'STOP_LOSS' if p<=sl else 'SELL_SIGNAL' if a.get('signal')=='SELL' else None
   if reason:
    gross=qty*p;f=gross*fee;net=gross-f;pnl=net-qty*entry;cash+=net;fees+=f;closed+=1;wins+=pnl>0;losses+=pnl<=0;logs.append({'side':'SELL','price':p,'pnl_usd':pnl,'reason':reason});qty=0;entry=0
  eq=cash+qty*p;peak=max(peak,eq);dd=max(dd,peak-eq)
 final=cash+qty*float(c.close.iloc[-1])
 return {'ok':True,'starting_usd':start,'final_usd':round(final,6),'pnl_usd':round(final-start,6),'return_pct':round((final/start-1)*100,4),'closed_trades':closed,'winning_trades':wins,'losing_trades':losses,'win_rate':round(wins/closed*100,2) if closed else 0,'max_drawdown_usd':round(dd,6),'fees_usd':round(fees,6),'trades':logs[-200:]}
