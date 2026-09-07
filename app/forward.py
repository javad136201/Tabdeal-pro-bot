
import threading, time

class ForwardRunner:
    def __init__(self, fetch_analysis, trader, interval=30):
        self.fetch_analysis=fetch_analysis
        self.trader=trader
        self.interval=interval
        self.running=False
        self.thread=None
        self.last_result=None
        self.last_error=None
        self.lock=threading.Lock()

    def tick(self):
        try:
            a=self.fetch_analysis()
            s=self.trader.tick(a)
            self.last_result={"analysis":a,"state":s,"updated":time.time()}
            self.last_error=None
            return self.last_result
        except Exception as e:
            self.last_error=str(e)
            return {"error":self.last_error}

    def _loop(self):
        while self.running:
            self.tick()
            time.sleep(self.interval)

    def start(self):
        with self.lock:
            if self.running: return
            self.running=True
            self.thread=threading.Thread(target=self._loop,daemon=True)
            self.thread.start()

    def stop(self):
        with self.lock:
            self.running=False

    def status(self):
        return {"running":self.running,"interval_sec":self.interval,"last_result":self.last_result,"last_error":self.last_error}
