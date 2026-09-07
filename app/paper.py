
from threading import RLock
import time
class PaperEngine:
    def __init__(self,start,trade,fee,tp,sl,trailing): self.lock=RLock(); self.start=start;self.trade=trade;self.fee=fee;self.default_tp=tp;self.default_sl=sl;self.default_trailing=trailing;self.reset()
    def reset(self):
        with self.lock:self.quote=self.start;self.base=0.;self.entry=0.;self.last=0.;self.realized=0.;self.fees=0.;self.trades=[];self.active=True;self.highest=0.;self.tp=self.default_tp;self.sl=self.default_sl;self.trailing=self.default_trailing;self.updated=time.time();return self.snapshot()
    def configure(self,tp=None,sl=None,trailing=None):
        with self.lock:
            if tp is not None:self.tp=max(0,float(tp))
            if sl is not None:self.sl=max(0,float(sl))
            if trailing is not None:self.trailing=max(0,float(trailing))
            return self.snapshot()
    def buy(self,p,reason='SIGNAL'):
        spend=min(self.trade,self.quote); fee=spend*self.fee; qty=(spend-fee)/p
        if qty<=0:return
        self.quote-=spend;self.base+=qty;self.entry=p;self.highest=p;self.fees+=fee;self.trades.append({'side':'BUY','price':p,'qty':qty,'quote':spend,'fee':fee,'pnl':0.,'reason':reason})
    def sell(self,p,reason):
        if self.base<=0:return
        qty=self.base;gross=qty*p;fee=gross*self.fee;net=gross-fee;pnl=net-qty*self.entry
        self.quote+=net;self.base=0;self.realized+=pnl;self.fees+=fee;self.trades.append({'side':'SELL','price':p,'qty':qty,'quote':gross,'fee':fee,'pnl':pnl,'reason':reason});self.entry=0;self.highest=0
    def process(self,a):
        with self.lock:
            p=a.get('price')
            if not p:return self.snapshot()
            p=float(p);self.last=p
            if not self.base and self.active and a.get('signal')=='BUY': self.buy(p)
            elif self.base:
                self.highest=max(self.highest,p)
                if self.tp and p>=self.entry*(1+self.tp/100):self.sell(p,'TAKE_PROFIT')
                elif self.sl and p<=self.entry*(1-self.sl/100):self.sell(p,'STOP_LOSS')
                elif self.trailing and self.highest>self.entry and p<=self.highest*(1-self.trailing/100):self.sell(p,'TRAILING_STOP')
                elif a.get('signal')=='SELL':self.sell(p,'SIGNAL')
            self.updated=time.time();return self.snapshot()
    def manual_close(self):
        with self.lock:
            if self.base:self.sell(self.last,'MANUAL_CLOSE')
            return self.snapshot()
    def snapshot(self):
        eq=self.quote+self.base*self.last;u=(self.last-self.entry)*self.base if self.base else 0
        return {'quote_balance':round(self.quote,8),'base_balance':round(self.base,10),'position':'LONG' if self.base else 'FLAT','entry_price':round(self.entry,8),'last_price':round(self.last,8),'take_profit':round(self.entry*(1+self.tp/100),8) if self.entry else 0,'stop_loss':round(self.entry*(1-self.sl/100),8) if self.entry else 0,'trailing_stop':round(self.highest*(1-self.trailing/100),8) if self.base and self.trailing else 0,'unrealized_pnl':round(u,8),'realized_pnl':round(self.realized,8),'total_pnl':round(eq-self.start,8),'equity':round(eq,8),'fees':round(self.fees,8),'trades_count':len(self.trades),'active':self.active,'tp_pct':self.tp,'sl_pct':self.sl,'trailing_pct':self.trailing,'trades':self.trades[-50:]}
