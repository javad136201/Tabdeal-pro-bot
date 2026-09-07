from .data import trades_to_candles
from .strategy import analyze

class MarketEngine:
    def analyze(self, raw_trades):
        candles = trades_to_candles(raw_trades)
        result = analyze(candles)
        result["engine"] = "v1.3-demo"
        return result
