from fastapi import FastAPI
from fastapi.responses import FileResponse
from .config import settings
from .tabdeal import recent_trades, ping
from .market_engine import MarketEngine
from .demo import DemoEngine
from .data import trades_to_candles

app = FastAPI(title="Tabdeal Pro Bot", version="1.3.0")
engine = MarketEngine()
demo = DemoEngine(
    start_quote=settings.demo_start_quote,
    trade_quote=settings.demo_trade_quote,
    fee_rate=settings.demo_fee_rate,
)

@app.get("/")
def root():
    return FileResponse("app/static/index.html")

@app.get("/health")
def health():
    return {"ok": True, "version": "1.3.0"}

@app.get("/api/status")
def status():
    return {
        "mode": settings.mode,
        "symbol": settings.symbol,
        "version": "1.3.0",
        "live_enabled": False,
        "demo_enabled": settings.demo_enabled,
    }

@app.get("/api/market")
def market():
    raw = recent_trades(settings.symbol, settings.market_limit)
    candles = trades_to_candles(raw)
    return {
        "symbol": settings.symbol,
        "trades": len(raw),
        "candles": len(candles),
        "last_price": float(candles["close"].iloc[-1]) if len(candles) else None,
    }

@app.get("/api/analysis")
def analysis():
    try:
        raw = recent_trades(settings.symbol, settings.market_limit)
        return engine.analyze(raw)
    except Exception as e:
        return {"signal":"HOLD", "confidence":0, "error":str(e)}

@app.post("/api/demo/tick")
def demo_tick():
    if not settings.demo_enabled:
        return {"ok": False, "error": "Demo trading is disabled"}
    a = analysis()
    state = demo.tick(a)
    return {"ok": True, "analysis": a, "demo": state}

@app.get("/api/demo/state")
def demo_state():
    return demo.snapshot()

@app.post("/api/demo/reset")
def demo_reset():
    return demo.reset()

@app.get("/api/backtest")
def backtest():
    # This endpoint is intentionally based on the currently available trade-derived candles.
    from .backtest import run_backtest
    raw = recent_trades(settings.symbol, settings.market_limit)
    candles = trades_to_candles(raw)
    return run_backtest(candles, starting_quote=settings.demo_start_quote, fee_rate=settings.demo_fee_rate)
