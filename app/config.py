import os
class Settings:
    app_version='4.1.0'; symbol=os.getenv('SYMBOL','BTC_USDT'); quote='USD'
    market_poll=float(os.getenv('MARKET_POLL_SECONDS','3')); bootstrap=int(os.getenv('BOOTSTRAP_TRADES','1000'))
    db=os.getenv('DB_PATH','/tmp/tabdeal_pro.db'); start=float(os.getenv('STARTING_USD','1000')); order=float(os.getenv('ORDER_USD','50')); fee=float(os.getenv('FEE_RATE','0.001'))
    profile=os.getenv('STRATEGY_PROFILE','BALANCED').upper(); min_conf=float(os.getenv('MIN_CONFIDENCE','65'))
    atr_mult=float(os.getenv('ATR_STOP_MULT','1.5')); rr=float(os.getenv('REWARD_RISK','2')); trail=float(os.getenv('TRAILING_PCT','0.5'))
    cooldown=int(os.getenv('COOLDOWN_SECONDS','60')); daily_loss=float(os.getenv('MAX_DAILY_LOSS_PCT','3')); max_day=int(os.getenv('MAX_TRADES_PER_DAY','20'))
    auto_demo=os.getenv('AUTO_DEMO','true').lower()=='true'; auto_forward=os.getenv('AUTO_FORWARD','true').lower()=='true'
    live_enabled=False
settings=Settings()

Settings.max_daily_loss_pct = Settings.daily_loss
Settings.max_trades_per_day = Settings.max_day
Settings.order_usd = Settings.order
Settings.fee_rate = Settings.fee
Settings.trailing_pct = Settings.trail
Settings.cooldown_seconds = Settings.cooldown
Settings.max_daily_loss = Settings.daily_loss
