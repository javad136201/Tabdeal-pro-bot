
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from .config import settings
from .storage import MarketStore
from .collector import Collector
from .strategy import signal
from .paper import PaperEngine
from .backtest import run as run_backtest
from .data import csv_to_ohlcv

app=FastAPI(title="Tabdeal Pro v4",version="4.0.0")
store=MarketStore(); collector=Collector(store); collector.start()
demo=PaperEngine("DEMO",settings.starting_usd,settings.order_usd,settings.fee_rate,trailing_pct=settings.trailing_pct,cooldown=settings.cooldown_seconds,max_daily_loss=settings.max_daily_loss_pct)
forward=PaperEngine("FORWARD",settings.starting_usd,settings.order_usd,settings.fee_rate,trailing_pct=settings.trailing_pct,cooldown=settings.cooldown_seconds,max_daily_loss=settings.max_daily_loss_pct)

@app.get("/")
def root():return FileResponse("app/static/index.html")
@app.get("/health")
def health():return {"ok":True,"version":"4.0.0","collector_running":collector.running,"last_error":collector.last_error}
@app.get("/api/status")
def status():
    return {"version":"4.0.0","symbol":settings.symbol,"base_currency":settings.symbol.split("_")[0],"quote_currency":"USDT","display_currency":"USD","mode":settings.mode,"live_locked":True,"live_enabled":False,"stored_1m":store.count(settings.symbol,"1m")}
def candles_data(limit=500):
    c=store.load(settings.symbol,"1m",limit)
    rows=[]
    for idx,r in c.iterrows():rows.append({"time":idx.isoformat(),"open":float(r.open),"high":float(r.high),"low":float(r.low),"close":float(r.close),"volume":float(r.volume)})
    return rows
@app.get("/api/candles")
def candles():return {"symbol":settings.symbol,"interval":"1m","candles":candles_data(500)}
@app.get("/api/analysis")
def analysis():
    c=store.load(settings.symbol,"1m",3000)
    return signal(c,settings.min_confidence)
@app.get("/api/strategy")
def strategy():return analysis()
@app.get("/api/demo/state")
def demo_state():return demo.snapshot()
@app.post("/api/demo/tick")
def demo_tick():
    a=analysis();return {"ok":True,"analysis":a,"state":demo.tick(a)}
@app.post("/api/demo/manual-close")
def demo_close():return demo.manual_close()
@app.post("/api/demo/reset")
def demo_reset():demo.reset();return demo.snapshot()
@app.get("/api/forward/state")
def forward_state():return forward.snapshot()
@app.post("/api/forward/tick")
def forward_tick():
    a=analysis();return {"ok":True,"analysis":a,"state":forward.tick(a)}
@app.post("/api/forward/manual-close")
def forward_close():return forward.manual_close()
@app.post("/api/forward/reset")
def forward_reset():forward.reset();return forward.snapshot()
@app.post("/api/backtest/upload")
async def backtest_upload(file:UploadFile=File(...)):
    try:
        c=csv_to_ohlcv(await file.read())
        return run_backtest(c,settings.starting_usd,settings.order_usd,settings.fee_rate,settings.min_confidence)
    except Exception as e:return {"ok":False,"error":str(e)}
@app.get("/api/live/preflight")
def live_preflight():return {"ok":False,"locked":True,"message":"Live هنوز قفل است؛ این نسخه برای اعتبارسنجی Demo و Forward طراحی شده است."}
