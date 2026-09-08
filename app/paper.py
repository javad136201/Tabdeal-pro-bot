
from threading import RLock
from datetime import datetime, timezone, date

class PaperEngine:
    def __init__(self,name,start_usd,order_usd,fee_rate,tp_pct=0,sl_pct=0,trailing_pct=.5,cooldown=60,max_daily_loss=3):
        self.name=name; self.start=start_usd; self.order_usd=order_usd; self.fee=fee_rate
        self.tp_pct=tp_pct; self.sl_pct=sl_pct; self.trailing_pct=trailing_pct
        self.cooldown=cooldown; self.max_daily_loss=max_daily_loss; self.lock=RLock(); self.reset()
    def reset(self):
        with self.lock:
            self.usd=self.start; self.qty=0.; self.entry=0.; self.last=0.; self.high=0.
            self.realized=0.; self.fees=0.; self.trades=[]; self.last_trade=0.; self.day=date.today()
            self.day_start=self.start; self.enabled=True
    def equity(self): return self.usd+self.qty*self.last
    def risk_blocked(self):
        if date.today()!=self.day:self.day=date.today(); self.day_start=self.equity()
        loss=(self.equity()-self.day_start)/self.day_start*100 if self.day_start else 0
        if loss<=-self.max_daily_loss:self.enabled=False
        return not self.enabled
    def buy(self,p,sl,tp,reason="SIGNAL"):
        import time
        now=time.time()
        if self.qty or self.risk_blocked() or now-self.last_trade<self.cooldown:return False
        spend=min(self.order_usd,self.usd); fee=spend*self.fee; qty=(spend-fee)/p
        self.usd-=spend; self.qty=qty; self.entry=p; self.high=p; self.fees+=fee; self.last_trade=now
        self.active_sl=sl; self.active_tp=tp
        self.trades.append({"side":"BUY","price":p,"qty":qty,"quote":spend,"fee":fee,"pnl":0.,"reason":reason,"time":datetime.now(timezone.utc).isoformat(),"sl":sl,"tp":tp})
        return True
    def sell(self,p,reason="SIGNAL"):
        if not self.qty:return False
        qty=self.qty; gross=qty*p; fee=gross*self.fee; net=gross-fee; pnl=net-qty*self.entry
        self.usd+=net; self.qty=0; self.entry=0; self.high=0; self.fees+=fee; self.realized+=pnl
        self.last_trade=__import__("time").time()
        self.trades.append({"side":"SELL","price":p,"qty":qty,"quote":gross,"fee":fee,"pnl":pnl,"reason":reason,"time":datetime.now(timezone.utc).isoformat()})
        return True
    def tick(self,a):
        p=a.get("price")
        if not p:return self.snapshot()
        p=float(p); self.last=p
        if self.qty==0:
            if a.get("signal")=="BUY":
                self.buy(p,a.get("suggested_sl",p*.99),a.get("suggested_tp",p*1.02))
        else:
            self.high=max(self.high,p)
            if p>=self.active_tp:self.sell(p,"TAKE_PROFIT")
            elif p<=self.active_sl:self.sell(p,"STOP_LOSS")
            else:
                # Activate a simple trailing stop after price moves 1R.
                r=self.active_tp-self.entry
                if r>0 and p>=self.entry+r*.5:
                    trail=self.high*(1-self.trailing_pct/100)
                    if p<=trail:self.sell(p,"TRAILING_STOP")
                elif a.get("signal")=="SELL":self.sell(p,"SIGNAL")
        return self.snapshot()
    def manual_close(self):
        if self.qty:self.sell(self.last,"MANUAL_CLOSE")
        return self.snapshot()
    def snapshot(self):
        eq=self.equity(); unreal=(self.last-self.entry)*self.qty if self.qty else 0
        return {"engine":self.name,"usd_balance":round(self.usd,6),"asset_qty":round(self.qty,10),
                "position":"LONG" if self.qty else "FLAT","entry_price":round(self.entry,8),
                "last_price":round(self.last,8),"stop_loss":round(getattr(self,"active_sl",0),8) if self.qty else 0,
                "take_profit":round(getattr(self,"active_tp",0),8) if self.qty else 0,
                "equity_usd":round(eq,6),"unrealized_usd":round(unreal,6),
                "realized_usd":round(self.realized,6),"total_pnl_usd":round(eq-self.start,6),
                "fees_usd":round(self.fees,6),"enabled":self.enabled,"trades_count":len(self.trades),
                "trades":self.trades[-50:]}
