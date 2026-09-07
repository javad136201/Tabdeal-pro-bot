
from threading import RLock,Thread,Event
import time
class ForwardTester:
    def __init__(self,market_fn,analysis_fn,poll=10):
        self.market_fn=market_fn;self.analysis_fn=analysis_fn;self.poll=poll;self.lock=RLock();self.running=False;self.event=Event();self.thread=None;self.reset()
    def reset(self):
        with self.lock:self.position=None;self.trades=[];self.equity=1000.;self.start=1000.;self.last_price=0.;self.last_signal='HOLD';self.high_water=1000.;self.max_dd=0;self.wins=0;self.losses=0
    def start(self):
        with self.lock:
            if self.running:return
            self.running=True;self.event.clear();self.thread=Thread(target=self._loop,daemon=True);self.thread.start()
    def stop(self):
        with self.lock:self.running=False;self.event.set()
    def _loop(self):
        while not self.event.wait(self.poll):
            try:self.tick()
            except Exception: pass
    def tick(self):
        raw=self.market_fn();a=self.analysis_fn(raw);p=a.get('price');
        if not p:return self.snapshot()
        with self.lock:
            p=float(p);self.last_price=p;self.last_signal=a.get('signal','HOLD')
            if self.position is None and a.get('signal')=='BUY':self.position={'entry':p}
            elif self.position is not None and a.get('signal')=='SELL':
                pnl=p-self.position['entry'];self.equity+=pnl;self.trades.append({'entry':self.position['entry'],'exit':p,'pnl':pnl,'result':'WIN' if pnl>0 else 'LOSS'});self.wins+=pnl>0;self.losses+=pnl<=0;self.position=None
            if self.position:self.marked=self.start+(p-self.position['entry'])
            else:self.marked=self.equity
            self.high_water=max(self.high_water,self.marked);self.max_dd=max(self.max_dd,self.high_water-self.marked)
            return self.snapshot()
    def snapshot(self):
        with self.lock:
            return {'running':self.running,'position':'LONG' if self.position else 'FLAT','last_price':self.last_price,'last_signal':self.last_signal,'equity':round(self.marked if hasattr(self,'marked') else self.start,8),'pnl':round((self.marked if hasattr(self,'marked') else self.start)-self.start,8),'closed_trades':len(self.trades),'win_rate':round(self.wins/len(self.trades)*100,2) if self.trades else 0,'max_drawdown':round(self.max_dd,8),'trades':self.trades[-50:]}
