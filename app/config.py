import os

class Settings:
    mode = os.getenv("TRADING_MODE", "DEMO").upper()
    symbol = os.getenv("SYMBOL", "BTC_USDT")
    api_key = os.getenv("TABDEAL_API_KEY", "")
    api_secret = os.getenv("TABDEAL_API_SECRET", "")
    market_limit = int(os.getenv("MARKET_LIMIT", "500"))
    demo_start_quote = float(os.getenv("DEMO_START_QUOTE", "1000"))
    demo_trade_quote = float(os.getenv("DEMO_TRADE_QUOTE", "50"))
    demo_fee_rate = float(os.getenv("DEMO_FEE_RATE", "0.001"))
    demo_enabled = os.getenv("DEMO_ENABLED", "true").lower() == "true"

settings = Settings()
