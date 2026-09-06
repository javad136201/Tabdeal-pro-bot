import os
from dataclasses import dataclass
@dataclass(frozen=True)
class Settings:
    trading_mode:str=os.getenv("TRADING_MODE","DEMO").upper()
    symbol:str=os.getenv("SYMBOL","BTC_USDT").upper()
    tabdeal_api_key:str=os.getenv("TABDEAL_API_KEY","")
    tabdeal_api_secret:str=os.getenv("TABDEAL_API_SECRET","")
    market_limit:int=int(os.getenv("MARKET_LIMIT","500"))
settings=Settings()
