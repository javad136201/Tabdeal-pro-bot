import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    app_env = os.getenv("APP_ENV", "local")
    secret_key = os.getenv("SECRET_KEY", "change-me")
    mode = os.getenv("TRADING_MODE", "DEMO").upper()
    base_url = os.getenv("TABDEAL_BASE_URL", "https://api1.tabdeal.org")
    symbol = os.getenv("SYMBOL", "BTCIRT").upper().replace("_","")
    trade_amount = float(os.getenv("TRADE_AMOUNT_IRT", "1000000"))
    fee_rate = float(os.getenv("FEE_RATE", "0.004"))
    rsi_buy = float(os.getenv("RSI_BUY", "55"))
    rsi_sell = float(os.getenv("RSI_SELL", "45"))
    min_score = int(os.getenv("MIN_SCORE", "4"))
    stop_loss_pct = float(os.getenv("STOP_LOSS_PCT", "1.2")) / 100
    take_profit_pct = float(os.getenv("TAKE_PROFIT_PCT", "2.4")) / 100
    max_daily_trades = int(os.getenv("MAX_DAILY_TRADES", "5"))

settings = Settings()
