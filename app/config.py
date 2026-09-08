
import os

class Settings:
    symbol=os.getenv("SYMBOL","BTC_USDT")
    mode=os.getenv("TRADING_MODE","DEMO").upper()
    poll_seconds=float(os.getenv("MARKET_POLL_SECONDS","3"))
    bootstrap_trades=int(os.getenv("BOOTSTRAP_TRADES","1000"))
    db_path=os.getenv("DB_PATH","/tmp/tabdeal_market.db")

    starting_usd=float(os.getenv("STARTING_USD","1000"))
    order_usd=float(os.getenv("ORDER_USD","50"))
    fee_rate=float(os.getenv("FEE_RATE","0.001"))

    min_confidence=float(os.getenv("MIN_CONFIDENCE","70"))
    risk_per_trade_pct=float(os.getenv("RISK_PER_TRADE_PCT","0.5"))
    atr_stop_mult=float(os.getenv("ATR_STOP_MULT","1.5"))
    rr_target=float(os.getenv("RR_TARGET","2.0"))
    trailing_trigger_r=float(os.getenv("TRAILING_TRIGGER_R","1.0"))
    trailing_pct=float(os.getenv("TRAILING_PCT","0.5"))
    cooldown_seconds=int(os.getenv("COOLDOWN_SECONDS","60"))
    max_daily_loss_pct=float(os.getenv("MAX_DAILY_LOSS_PCT","3"))

    live_enabled=os.getenv("LIVE_TRADING_ENABLED","false").lower()=="true"

settings=Settings()
