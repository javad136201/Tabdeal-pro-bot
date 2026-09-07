from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from .config import settings
from .tabdeal import recent_trades
from .data import trades_to_candles, normalize_ohlcv_csv
from .strategy import analyze
from .trader import PaperTrader
from .backtest import run_backtest
from .forward import ForwardRunner

app = FastAPI(title="Tabdeal Pro", version="3.2.0")


def get_candles(limit=120):
    raw = recent_trades(settings.symbol, settings.market_limit)
    return trades_to_candles(raw).tail(limit)


def market_analysis():
    candles = get_candles(120)
    return analyze(candles, settings.min_confidence)


def demo_factory(name):
    return PaperTrader(name, settings.demo_start_quote, settings.order_quote,
                       settings.fee_rate, settings.tp_pct, settings.sl_pct,
                       settings.trailing_pct, settings.cooldown_sec,
                       settings.max_daily_loss_pct)


demo = demo_factory("DEMO")
forward = demo_factory("FORWARD")
runner = ForwardRunner(market_analysis, forward, settings.forward_interval_sec)

@app.get("/")
def root(): return FileResponse("app/static/index.html")

@app.get("/health")
def health(): return {"ok": True, "version": "3.2.0"}

@app.get("/api/status")
def status():
    return {"version":"3.2.0","symbol":settings.symbol,"quote_currency":"USDT",
            "display_currency":"USD/USDT","mode":settings.mode,
            "live_enabled":settings.live_enabled,"live_locked":True}

@app.get("/api/analysis")
def analysis():
    try: return market_analysis()
    except Exception as e: return {"signal":"HOLD","confidence":0,"error":str(e)}

@app.get("/api/candles")
def candles():
    try:
        c=get_candles(140)
        rows=[]
        for idx,row in c.iterrows():
            rows.append({"time":idx.isoformat(),"open":float(row.open),"high":float(row.high),"low":float(row.low),"close":float(row.close),"volume":float(row.volume)})
        return {"symbol":settings.symbol,"interval":"1m","quote_currency":"USDT","candles":rows}
    except Exception as e:
        return {"symbol":settings.symbol,"interval":"1m","candles":[],"error":str(e)}

@app.get("/api/demo/state")
def demo_state(): return demo.snapshot()
@app.post("/api/demo/tick")
def demo_tick():
    a=market_analysis(); return {"ok":True,"analysis":a,"state":demo.tick(a)}
@app.post("/api/demo/manual-close")
def demo_close(): return demo.manual_close()
@app.post("/api/demo/reset")
def demo_reset(): demo.reset(); return demo.snapshot()
@app.post("/api/demo/settings")
def demo_settings(payload:dict):
    allowed={k:payload[k] for k in ("order_quote","tp_pct","sl_pct","trailing_pct","cooldown_sec","max_daily_loss_pct") if k in payload}
    return demo.update_settings(**allowed)

@app.get("/api/forward/state")
def forward_state(): return {"runner":runner.status(),"state":forward.snapshot()}
@app.post("/api/forward/tick")
def forward_tick(): return {"ok":True,"result":runner.tick()}
@app.post("/api/forward/start")
def forward_start(): runner.start(); return runner.status()
@app.post("/api/forward/stop")
def forward_stop(): runner.stop(); return runner.status()
@app.post("/api/forward/manual-close")
def forward_close(): return forward.manual_close()
@app.post("/api/forward/reset")
def forward_reset(): runner.stop(); forward.reset(); return forward.snapshot()
@app.post("/api/forward/settings")
def forward_settings(payload:dict):
    allowed={k:payload[k] for k in ("order_quote","tp_pct","sl_pct","trailing_pct","cooldown_sec","max_daily_loss_pct") if k in payload}
    return forward.update_settings(**allowed)

@app.get("/api/backtest/recent")
def backtest_recent():
    try:
        c=get_candles(180)
        return run_backtest(c,settings.demo_start_quote,settings.order_quote,settings.fee_rate,settings.tp_pct,settings.sl_pct,settings.trailing_pct,settings.min_confidence)
    except Exception as e: return {"ok":False,"error":str(e)}

@app.post("/api/backtest/upload")
async def backtest_upload(file: UploadFile = File(...)):
    try:
        c=normalize_ohlcv_csv(await file.read())
        return run_backtest(c,settings.demo_start_quote,settings.order_quote,settings.fee_rate,settings.tp_pct,settings.sl_pct,settings.trailing_pct,settings.min_confidence)
    except Exception as e: return {"ok":False,"error":str(e)}

@app.get("/api/live/preflight")
def live_preflight():
    return {"ok":False,"locked":True,"message":"Live در نسخه 3.2 قفل است؛ ابتدا Demo و Forward Test باید اعتبارسنجی شوند."}
