
import os

class Settings:
    mode = os.getenv("TRADING_MODE", "DEMO").upper()
    symbol = os.getenv("SYMBOL", "BTC_USDT")
    market_limit = int(os.getenv("MARKET_LIMIT", "800"))
    demo_start_quote = float(os.getenv("DEMO_START_QUOTE", "1000"))
    order_quote = float(os.getenv("ORDER_QUOTE", "50"))
    fee_rate = float(os.getenv("FEE_RATE", "0.001"))
    tp_pct = float(os.getenv("DEFAULT_TP_PCT", "1.5"))
    sl_pct = float(os.getenv("DEFAULT_SL_PCT", "1.0"))
    trailing_pct = float(os.getenv("DEFAULT_TRAILING_PCT", "0.5"))
    cooldown_sec = int(os.getenv("COOLDOWN_SEC", "60"))
    min_confidence = float(os.getenv("MIN_CONFIDENCE", "60"))
    max_daily_loss_pct = float(os.getenv("MAX_DAILY_LOSS_PCT", "3"))
    forward_interval_sec = int(os.getenv("FORWARD_INTERVAL_SEC", "30"))
    quote_currency = "USDT"
    display_currency = "USD/USDT"
    live_enabled = os.getenv("LIVE_TRADING_ENABLED", "false").lower() == "true"

settings = Settings()
