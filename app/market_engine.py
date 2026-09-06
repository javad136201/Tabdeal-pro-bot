from .data import trades_to_candles
from .strategy import analyze_dataframe
class MarketEngine:
    def analyze(self,trades): return analyze_dataframe(trades_to_candles(trades))
