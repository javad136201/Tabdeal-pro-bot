import os
class Settings:
    mode=os.getenv("TRADING_MODE","DEMO").upper(); symbol=os.getenv("SYMBOL","BTC_USDT")
    api_key=os.getenv("TABDEAL_API_KEY",""); api_secret=os.getenv("TABDEAL_API_SECRET","")
    market_limit=int(os.getenv("MARKET_LIMIT","1000")); candle_minutes=int(os.getenv("CANDLE_MINUTES","1"))
    demo_start_quote=float(os.getenv("DEMO_START_QUOTE","1000")); trade_quote=float(os.getenv("TRADE_QUOTE","50")); fee_rate=float(os.getenv("FEE_RATE","0.001"))
    auto_trading=os.getenv("AUTO_TRADING","false").lower()=="true"
    live_enabled=os.getenv("LIVE_TRADING_ENABLED","false").lower()=="true"
    live_confirmation=os.getenv("LIVE_CONFIRMATION","")
    # UI-only defaults; can be overridden per Demo position from dashboard
    default_take_profit_pct=float(os.getenv("DEFAULT_TAKE_PROFIT_PCT","2")); default_stop_loss_pct=float(os.getenv("DEFAULT_STOP_LOSS_PCT","1"))
    max_daily_loss=float(os.getenv("MAX_DAILY_LOSS","20")); max_trades_per_day=int(os.getenv("MAX_TRADES_PER_DAY","10")); cooldown_seconds=int(os.getenv("COOLDOWN_SECONDS","300"))
    state_file=os.getenv("STATE_FILE","/tmp/tabdeal_bot_state.json")
settings=Settings()
