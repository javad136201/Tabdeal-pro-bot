from .data import trades_to_candles
from .strategy import signal
class MarketEngine:
    def analyze(self,trades):
        df=trades_to_candles(trades)
        if df.empty:return {'signal':'HOLD','confidence':0}
        r=signal(df); r['confidence']=min(95,50+abs(r.get('score',0))*25); return r
