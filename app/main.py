from fastapi import FastAPI
from fastapi.responses import FileResponse
from .config import settings
from .tabdeal import recent_trades
from .data import trades_to_candles
from .strategy import analyze
from .demo import DemoEngine
app=FastAPI(title="Tabdeal Pro Final",version="2.0.0")
demo=DemoEngine(settings.demo_start_quote,settings.demo_trade_quote,settings.fee_rate,settings.tp_pct,settings.sl_pct)
def get_a(): return analyze(trades_to_candles(recent_trades(settings.symbol,settings.market_limit)))
@app.get("/")
def root(): return FileResponse("app/static/index.html")
@app.get("/health")
def health(): return {"ok":True,"version":"2.0.0"}
@app.get("/api/status")
def status(): return {"mode":settings.mode,"symbol":settings.symbol,"version":"2.0.0","live_enabled":settings.live_enabled,"demo_enabled":settings.demo_enabled}
@app.get("/api/analysis")
def analysis():
    try:return get_a()
    except Exception as e:return {"signal":"HOLD","confidence":0,"error":str(e)}
@app.get("/api/demo/state")
def state():return demo.snapshot()
@app.post("/api/demo/tick")
def tick():return {"ok":True,"analysis":get_a(),"demo":demo.tick(get_a())}
@app.post("/api/demo/manual-close")
def close():return demo.manual_close()
@app.post("/api/demo/reset")
def reset():return demo.reset()
@app.get("/api/live/preflight")
def preflight():return {"ok":False,"live_enabled":settings.live_enabled,"message":"معاملات واقعی عمداً قفل هستند."}
