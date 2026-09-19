import time, threading, copy

class Paper:
    def __init__(self, balance, trade_usd, tp_pct, sl_pct, fee_pct, max_trades, max_loss, min_confidence=65):
        self.lock=threading.RLock()
        self.start_balance=balance; self.balance=balance; self.trade_usd=trade_usd
        self.tp_pct=tp_pct; self.sl_pct=sl_pct; self.fee_pct=fee_pct
        self.max_trades=max_trades; self.max_loss=max_loss
        self.min_confidence=min_confidence
        self.position=None; self.trades=[]; self.running=False
        self.last_error=""; self.last_action=""

    def reset(self):
        with self.lock:
            self.balance=self.start_balance; self.position=None; self.trades=[]
            self.last_error=""; self.last_action="RESET"

    def _today_count(self):
        day=time.strftime("%Y-%m-%d")
        return sum(1 for x in self.trades if x["time"][:10]==day)

    def _realized_today(self):
        day=time.strftime("%Y-%m-%d")
        return sum(x["pnl"] for x in self.trades if x["time"][:10]==day)

    def buy(self, price, reason="signal"):
        with self.lock:
            if self.position or self._today_count()>=self.max_trades or self._realized_today()<=-self.max_loss:
                return False
            usd=min(self.trade_usd,self.balance)
            if usd<=0:return False
            qty=usd/price
            fee=usd*self.fee_pct/100
            self.balance-=fee
            self.position={"side":"LONG","qty":qty,"entry":price,
                           "tp":price*(1+self.tp_pct/100),"sl":price*(1-self.sl_pct/100),
                           "cost":usd,"fee":fee,"opened":time.time(),"reason":reason}
            self.last_action="BUY"
            return True

    def close(self, price, reason="manual"):
        with self.lock:
            if not self.position:return False
            p=self.position
            gross=(price-p["entry"])*p["qty"]
            fee=(price*p["qty"])*self.fee_pct/100
            pnl=gross-p["fee"]-fee
            self.balance+=gross-fee
            self.trades.append({
                "time":time.strftime("%Y-%m-%d %H:%M:%S"),
                "side":"SELL","entry":p["entry"],"exit":price,"qty":p["qty"],
                "pnl":round(pnl,4),"reason":reason
            })
            self.position=None; self.last_action="SELL"
            return True

    def tick(self, price, signal, confidence):
        if not price:return self.snapshot(price)
        with self.lock:
            if self.position:
                p=self.position
                if price>=p["tp"]: self.close(price,"TP")
                elif price<=p["sl"]: self.close(price,"SL")
            if not self.position and signal=="BUY" and confidence>=self.min_confidence:
                self.buy(price,"strategy")
            return self.snapshot(price)

    def snapshot(self, price=None):
        with self.lock:
            pos=copy.deepcopy(self.position)
            unreal=0
            if pos and price: unreal=(price-pos["entry"])*pos["qty"]
            realized=sum(x["pnl"] for x in self.trades)
            return {"balance_usd":round(self.balance,4),"position":pos,
                    "unrealized_pnl_usd":round(unreal,4),
                    "realized_pnl_usd":round(realized,4),
                    "equity_usd":round(self.balance+unreal,4),
                    "trades":list(reversed(self.trades[-30:])),
                    "running":self.running,"last_action":self.last_action,
                    "last_error":self.last_error}
