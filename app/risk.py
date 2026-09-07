import time
class Risk:
 def __init__(self,max_loss=20,max_trades=10,cooldown=300): self.max_loss=max_loss;self.max_trades=max_trades;self.cooldown=cooldown;self.start=None;self.trades=0;self.last=0;self.stop=False
 def allow(self,equity):
  if self.stop:return False,"EMERGENCY_STOP"
  if self.start is None:self.start=equity
  if self.start-equity>=self.max_loss:return False,"DAILY_LOSS_LIMIT"
  if self.trades>=self.max_trades:return False,"MAX_TRADES_PER_DAY"
  if time.time()-self.last<self.cooldown:return False,"COOLDOWN"
  return True,"OK"
 def record(self): self.trades+=1;self.last=time.time()
