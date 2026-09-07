
import os
class Settings:
    mode=os.getenv('TRADING_MODE','DEMO').upper()
    symbol=os.getenv('SYMBOL','BTC_USDT')
    market_limit=int(os.getenv('MARKET_LIMIT','500'))
    poll_seconds=int(os.getenv('POLL_SECONDS','10'))
    demo_start_quote=float(os.getenv('DEMO_START_QUOTE','1000'))
    demo_trade_quote=float(os.getenv('DEMO_TRADE_QUOTE','50'))
    fee_rate=float(os.getenv('FEE_RATE','0.001'))
    tp_pct=float(os.getenv('DEFAULT_TP_PCT','1.5'))
    sl_pct=float(os.getenv('DEFAULT_SL_PCT','1.0'))
    trailing_pct=float(os.getenv('DEFAULT_TRAILING_PCT','0.5'))
    demo_enabled=os.getenv('DEMO_ENABLED','true').lower()=='true'
    forward_enabled=os.getenv('FORWARD_ENABLED','true').lower()=='true'
    live_enabled=os.getenv('LIVE_TRADING_ENABLED','false').lower()=='true'
    live_use_oco=os.getenv('LIVE_USE_OCO','true').lower()=='true'
    api_key=os.getenv('TABDEAL_API_KEY','')
    api_secret=os.getenv('TABDEAL_API_SECRET','')
    dashboard_password=os.getenv('DASHBOARD_PASSWORD','')
settings=Settings()
