from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from .config import settings
from .tabdeal import TabdealClient
from .market_engine import MarketEngine
app=FastAPI(title="Tabdeal Pro Bot",version="1.2.1")
client=TabdealClient(settings.tabdeal_api_key,settings.tabdeal_api_secret); engine=MarketEngine()
@app.get("/",response_class=HTMLResponse)
def home(): return open("app/static/index.html",encoding="utf-8").read()
@app.get("/api/status")
def status(): return {"mode":settings.trading_mode,"symbol":settings.symbol,"version":"1.2.1","live_enabled":settings.trading_mode=="LIVE"}
@app.get("/api/market")
def market():
    t=client.recent_trades(settings.symbol,settings.market_limit)
    return {"symbol":settings.symbol,"trade_count":len(t),"last_trade":t[-1] if t else None}
@app.get("/api/analysis")
def analysis():
    try:
        r=engine.analyze(client.recent_trades(settings.symbol,settings.market_limit))
        r.update({"symbol":settings.symbol,"mode":settings.trading_mode,"version":"1.2.1"}); return r
    except Exception as e:
        return {"symbol":settings.symbol,"mode":settings.trading_mode,"version":"1.2.1","signal":"HOLD","confidence":0,"error":str(e)}
@app.get("/health")
def health(): return {"ok":True,"version":"1.2.1"}
