import os

class Settings:
    def __init__(self):
        self.symbol = os.getenv("SYMBOL", "BTC_USDT")
        self.demo_start = os.getenv("DEMO_START", "true").lower() == "true"
        self.demo_balance = float(os.getenv("DEMO_BALANCE_USD", "1000"))
        self.trade_usd = float(os.getenv("DEMO_TRADE_USD", "50"))
        self.tp_pct = float(os.getenv("TP_PCT", "1.0"))
        self.sl_pct = float(os.getenv("SL_PCT", "0.6"))
        self.fee_pct = float(os.getenv("FEE_PCT", "0.1"))
        self.interval = float(os.getenv("LOOP_SECONDS", "5"))
        self.min_confidence = float(os.getenv("MIN_CONFIDENCE", "65"))
        self.max_trades_day = int(os.getenv("MAX_TRADES_DAY", "20"))
        self.max_daily_loss = float(os.getenv("MAX_DAILY_LOSS_USD", "30"))
        self.api_base = os.getenv("TABDEAL_BASE_URL", "https://api1.tabdeal.org")

settings = Settings()
