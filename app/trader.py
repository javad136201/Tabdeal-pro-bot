
from threading import RLock
from datetime import datetime, timezone, date

class PaperTrader:
    def __init__(self, name, start_quote, order_quote, fee_rate, tp_pct, sl_pct, trailing_pct, cooldown_sec, max_daily_loss_pct):
        self.name=name
        self.start_quote=start_quote
        self.order_quote=order_quote
        self.fee_rate=fee_rate
        self.tp_pct=tp_pct
        self.sl_pct=sl_pct
        self.trailing_pct=trailing_pct
        self.cooldown_sec=cooldown_sec
        self.max_daily_loss_pct=max_daily_loss_pct
        self.lock=RLock()
        self.reset()

    def reset(self):
        with self.lock:
            self.quote=self.start_quote
            self.base=0.0
            self.entry=0.0
            self.last_price=0.0
            self.highest=0.0
            self.realized=0.0
            self.fees=0.0
            self.trades=[]
            self.enabled=True
            self.last_trade_ts=0.0
            self.day=date.today()
            self.day_start_equity=self.start_quote

    def _day_guard(self):
        today=date.today()
        if today != self.day:
            self.day=today
            self.day_start_equity=self.equity()
        loss_pct=((self.equity()-self.day_start_equity)/self.day_start_equity*100) if self.day_start_equity else 0
        return loss_pct <= -self.max_daily_loss_pct

    def _cooldown_ok(self, now):
        return now-self.last_trade_ts >= self.cooldown_sec

    def buy(self, price, now):
        spend=min(self.order_quote,self.quote)
        if spend<=0 or not self.enabled or not self._cooldown_ok(now): return False
        fee=spend*self.fee_rate
        qty=(spend-fee)/price
        self.quote-=spend
        self.base+=qty
        self.entry=price
        self.highest=price
        self.fees+=fee
        self.last_trade_ts=now
        self.trades.append({"side":"BUY","price":price,"qty":qty,"quote":spend,"fee":fee,"pnl":0.0,"reason":"SIGNAL","time":datetime.now(timezone.utc).isoformat()})
        return True

    def sell(self, price, reason, now):
        if self.base<=0: return False
        if self._day_guard() and reason=="SIGNAL":
            return False
        qty=self.base
        gross=qty*price
        fee=gross*self.fee_rate
        net=gross-fee
        pnl=net-qty*self.entry
        self.quote+=net
        self.base=0.0
        self.entry=0.0
        self.highest=0.0
        self.fees+=fee
        self.realized+=pnl
        self.last_trade_ts=now
        self.trades.append({"side":"SELL","price":price,"qty":qty,"quote":gross,"fee":fee,"pnl":pnl,"reason":reason,"time":datetime.now(timezone.utc).isoformat()})
        return True

    def tick(self, analysis):
        with self.lock:
            p=analysis.get("price")
            if not p: return self.snapshot()
            now=datetime.now(timezone.utc).timestamp()
            p=float(p)
            self.last_price=p
            if self._day_guard():
                self.enabled=False
            signal=analysis.get("signal","HOLD")
            if self.base<=0 and signal=="BUY":
                self.buy(p,now)
            elif self.base>0:
                self.highest=max(self.highest,p)
                tp=self.entry*(1+self.tp_pct/100)
                sl=self.entry*(1-self.sl_pct/100)
                trail=self.highest*(1-self.trailing_pct/100) if self.highest else 0
                if p>=tp: self.sell(p,"TAKE_PROFIT",now)
                elif p<=sl: self.sell(p,"STOP_LOSS",now)
                elif trail and p<=trail: self.sell(p,"TRAILING_STOP",now)
                elif signal=="SELL": self.sell(p,"SIGNAL",now)
            return self.snapshot()

    def manual_close(self):
        with self.lock:
            if self.base>0:
                self.sell(self.last_price,"MANUAL_CLOSE",datetime.now(timezone.utc).timestamp())
            return self.snapshot()

    def equity(self):
        return self.quote+self.base*self.last_price

    def snapshot(self):
        eq=self.equity()
        unreal=(self.last_price-self.entry)*self.base if self.base and self.entry else 0
        return {
            "name":self.name,"quote_balance":round(self.quote,8),"base_balance":round(self.base,10),
            "position":"LONG" if self.base>0 else "FLAT","entry_price":round(self.entry,8),
            "last_price":round(self.last_price,8),"take_profit":round(self.entry*(1+self.tp_pct/100),8) if self.entry else 0,
            "stop_loss":round(self.entry*(1-self.sl_pct/100),8) if self.entry else 0,
            "trailing_stop":round(self.highest*(1-self.trailing_pct/100),8) if self.highest else 0,
            "unrealized_pnl":round(unreal,8),"realized_pnl":round(self.realized,8),
            "total_pnl":round(eq-self.start_quote,8),"equity":round(eq,8),"fees":round(self.fees,8),
            "enabled":self.enabled,"trades_count":len(self.trades),"trades":self.trades[-25:],
            "settings":{"order_quote":self.order_quote,"tp_pct":self.tp_pct,"sl_pct":self.sl_pct,"trailing_pct":self.trailing_pct,"cooldown_sec":self.cooldown_sec,"max_daily_loss_pct":self.max_daily_loss_pct}
        }

    def update_settings(self, order_quote=None, tp_pct=None, sl_pct=None, trailing_pct=None, cooldown_sec=None, max_daily_loss_pct=None):
        with self.lock:
            if order_quote is not None: self.order_quote=max(0.0,float(order_quote))
            if tp_pct is not None: self.tp_pct=max(0.0,float(tp_pct))
            if sl_pct is not None: self.sl_pct=max(0.0,float(sl_pct))
            if trailing_pct is not None: self.trailing_pct=max(0.0,float(trailing_pct))
            if cooldown_sec is not None: self.cooldown_sec=max(0,int(cooldown_sec))
            if max_daily_loss_pct is not None: self.max_daily_loss_pct=max(0.0,float(max_daily_loss_pct))
            return self.snapshot()
