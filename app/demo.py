from threading import Lock
class DemoEngine:
    def __init__(self,start,trade,fee,tp,sl):
        self.start=start; self.trade=trade; self.fee=fee; self.tp=tp; self.sl=sl; self.lock=Lock(); self.reset()
    def reset(self):
        with self.lock:
            self.quote=self.start; self.base=0; self.entry=0; self.last=0; self.realized=0; self.fees=0; self.trades=[]
            return self.snapshot()
    def buy(self,p):
        spend=min(self.trade,self.quote); fee=spend*self.fee; qty=(spend-fee)/p
        self.quote-=spend; self.base=qty; self.entry=p; self.fees+=fee
        self.trades.append({"side":"BUY","price":p,"qty":qty,"quote":spend,"fee":fee,"pnl":0,"reason":"SIGNAL"})
    def sell(self,p,reason):
        if not self.base:return
        qty=self.base; gross=qty*p; fee=gross*self.fee; net=gross-fee; pnl=net-qty*self.entry
        self.quote+=net; self.base=0; self.fees+=fee; self.realized+=pnl
        self.trades.append({"side":"SELL","price":p,"qty":qty,"quote":gross,"fee":fee,"pnl":pnl,"reason":reason}); self.entry=0
    def tick(self,a):
        with self.lock:
            p=a.get("price")
            if not p:return self.snapshot()
            p=float(p); self.last=p
            if not self.base and a.get("signal")=="BUY": self.buy(p)
            elif self.base:
                if p>=self.entry*(1+self.tp/100): self.sell(p,"TAKE_PROFIT")
                elif p<=self.entry*(1-self.sl/100): self.sell(p,"STOP_LOSS")
                elif a.get("signal")=="SELL": self.sell(p,"SIGNAL")
            return self.snapshot()
    def manual_close(self):
        with self.lock:
            if self.base:self.sell(self.last,"MANUAL_CLOSE")
            return self.snapshot()
    def snapshot(self):
        equity=self.quote+self.base*self.last; unreal=(self.last-self.entry)*self.base if self.base else 0
        return {"quote_balance":round(self.quote,8),"base_balance":round(self.base,10),"position":"LONG" if self.base else "FLAT","entry_price":round(self.entry,8),"last_price":round(self.last,8),"take_profit":round(self.entry*(1+self.tp/100),8) if self.entry else 0,"stop_loss":round(self.entry*(1-self.sl/100),8) if self.entry else 0,"unrealized_pnl":round(unreal,8),"realized_pnl":round(self.realized,8),"total_pnl":round(equity-self.start,8),"equity":round(equity,8),"fees":round(self.fees,8),"trades_count":len(self.trades),"trades":self.trades[-20:]}
