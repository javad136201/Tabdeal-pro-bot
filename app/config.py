import os
class Settings:
    trading_mode=os.getenv('TRADING_MODE','DEMO')
    symbol=os.getenv('SYMBOL','BTC_USDT')
    tabdeal_api_key=os.getenv('TABDEAL_API_KEY','')
    tabdeal_api_secret=os.getenv('TABDEAL_API_SECRET','')
    live_armed=os.getenv('LIVE_ARMED','false').lower()=='true'
settings=Settings()
