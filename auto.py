import threading,time
class Auto:
    def __init__(self,name,fetch,engine,interval): self.name=name;self.fetch=fetch;self.engine=engine;self.interval=interval;self.running=False;self.last=None;self.error=None;self._thread=None
    def once(self):
        try:
            a=self.fetch(); self.last={'analysis':a,'state':self.engine.tick(a)}; self.error=None; return self.last
        except Exception as e:
            self.error=str(e); return {'error':self.error,'last':self.last}
    def loop(self):
        while self.running:
            self.once(); time.sleep(self.interval)
    def start(self):
        if self.running:return
        self.running=True; self._thread=threading.Thread(target=self.loop,daemon=True); self._thread.start()
    def stop(self): self.running=False
