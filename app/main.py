from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from .config import settings
from .tabdeal import TabdealClient
from .market_engine import MarketEngine
app=FastAPI(); client=TabdealClient(); engine=MarketEngine()
@app.get('/',response_class=HTMLResponse)
def home(): return open('app/static/index.html').read()
@app.get('/api/status')
def status(): return {'mode':settings.trading_mode,'symbol':settings.symbol}
@app.get('/api/analysis')
def analysis(): return engine.analyze(client.recent_trades(settings.symbol,500))
