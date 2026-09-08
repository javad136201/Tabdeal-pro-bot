import threading,time
class Auto:
    def __init__(self,name,fetch,engine,interval):self.name=name;self.fetch=fetch;self.engine=engine;self.interval=interval;self.running=False;self.last=None;self.error=None
    def once(self):
        try:a=self.fetch();self.last={'analysis':a,'state':self.engine.tick(a)};self.error=None;return self.last
        except Exception as e:self.error=str(e);return {'error':self.error}
    def loop(self):
        while self.running:self.once();time.sleep(self.interval)
    def start(self):
        if not self.running:self.running=True;threading.Thread(target=self.loop,daemon=True).start()
    def stop(self):self.running=False
