
import threading,time
from .config import settings
from .tabdeal import recent_trades
from .data import trades_to_1m
from .storage import MarketStore

class Collector:
    def __init__(self,store):
        self.store=store; self.running=False; self.thread=None; self.last_error=None; self.last_ok=0
    def once(self):
        raw=recent_trades(settings.symbol,settings.bootstrap_trades)
        c=trades_to_1m(raw)
        self.store.upsert(settings.symbol,"1m",c)
        self.last_ok=time.time();self.last_error=None
    def loop(self):
        while self.running:
            try:self.once()
            except Exception as e:self.last_error=str(e)
            time.sleep(settings.poll_seconds)
    def start(self):
        if self.running:return
        self.running=True; self.thread=threading.Thread(target=self.loop,daemon=True);self.thread.start()
    def stop(self):self.running=False
