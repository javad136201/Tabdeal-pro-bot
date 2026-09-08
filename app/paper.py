import time
class Paper:
    def __init__(self,name,start,order,fee,store,cfg):self.name=name;self.start=start;self.order=order;self.fee=fee;self.store=store;self.cfg=cfg;self.reset()
    def reset(self):self.usd=self.start;self.qty=0.;self.entry=0.;self.last=0.;self.sl=self.tp=0.;self.high=0.;self.realized=0.;self.fees=0.;self.trades=[];self.enabled=True;self.last_trade=0.;self.today_trades=0;self.day_start=self.start
    def equity(self):return self.usd+self.qty*self.last
    def buy(self,p,sl,tp):
        if self.qty or not self.enabled or time.time()-self.last_trade<self.cfg.cooldown:return False
        spend=min(self.order,self.usd);f=spend*self.fee;q=(spend-f)/p
        if q<=0:return False
        self.usd-=spend;self.qty=q;self.entry=p;self.high=p;self.sl=sl;self.tp=tp;self.fees+=f;self.last_trade=time.time();self.today_trades+=1
        e={'side':'BUY','price':p,'qty':q,'quote_usd':spend,'fee_usd':f,'pnl_usd':0,'reason':'SIGNAL'};self.trades.append(e);self.store.log(self.name,'BUY',e);return True
    def sell(self,p,reason):
        if not self.qty:return False
        q=self.qty;gross=q*p;f=gross*self.fee;net=gross-f;pnl=net-q*self.entry;self.usd+=net;self.qty=0;self.entry=0;self.high=0;self.fees+=f;self.realized+=pnl;self.last_trade=time.time();self.today_trades+=1
        e={'side':'SELL','price':p,'qty':q,'quote_usd':gross,'fee_usd':f,'pnl_usd':pnl,'reason':reason};self.trades.append(e);self.store.log(self.name,'SELL',e);return True
    def tick(self,a):
        p=a.get('price');
        if not p:return self.snapshot()
        self.last=float(p)
        if not self.qty:
            if a.get('signal')=='BUY':self.buy(self.last,float(a.get('suggested_sl',self.last*.995)),float(a.get('suggested_tp',self.last*1.01)))
        else:
            self.high=max(self.high,self.last)
            if self.last>=self.tp:self.sell(self.last,'TAKE_PROFIT')
            elif self.last<=self.sl:self.sell(self.last,'STOP_LOSS')
            elif a.get('signal')=='SELL':self.sell(self.last,'SELL_SIGNAL')
        return self.snapshot()
    def manual_close(self):self.sell(self.last,'MANUAL_CLOSE');return self.snapshot()
    def snapshot(self):
        eq=self.equity();return {'engine':self.name,'usd_balance':round(self.usd,6),'asset_qty':round(self.qty,10),'position':'LONG' if self.qty else 'FLAT','entry_price':round(self.entry,8),'last_price':round(self.last,8),'stop_loss':round(self.sl,8) if self.qty else 0,'take_profit':round(self.tp,8) if self.qty else 0,'equity_usd':round(eq,6),'unrealized_usd':round((self.last-self.entry)*self.qty,6) if self.qty else 0,'realized_usd':round(self.realized,6),'total_pnl_usd':round(eq-self.start,6),'fees_usd':round(self.fees,6),'trades_count':len(self.trades),'enabled':self.enabled,'trades':self.trades[-50:]}
