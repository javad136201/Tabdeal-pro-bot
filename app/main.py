import asyncio, csv, io, time
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .tabdeal import Tabdeal
from .market import normalize_trades, candles
from .strategy import analyze
from .paper import Paper
from .backtest import run as run_backtest

app=FastAPI(title="Tabdeal Pro Clean",version="5.0.0")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])

client=Tabdeal(settings.api_base)
paper=Paper(settings.demo_balance,settings.trade_usd,settings.tp_pct,settings.sl_pct,
            settings.fee_pct,settings.max_trades_day,settings.max_daily_loss)

state={"running":False,"last_price":None,"last_analysis":{},"candles":[],"error":"",
       "last_update":None,"market_ok":False}

@app.get("/")
def home(): return FileResponse(Path(__file__).parent/"static"/"index.html")

@app.get("/api/health")
def health(): return {"ok":True,"version":"5.0.0"}

@app.get("/api/status")
def status():
    return {"ok":True,"version":"5.0.0","symbol":settings.symbol,
            "demo_running":state["running"],"market_ok":state["market_ok"],
            "last_update":state["last_update"],"error":state["error"]}

@app.get("/api/market")
def market():
    return {"symbol":settings.symbol,"price":state["last_price"],
            "candles":state["candles"][-180:],"error":state["error"]}

@app.get("/api/analysis")
def api_analysis():
    return state["last_analysis"] or {"signal":"HOLD","confidence":0,"reason":"در حال دریافت بازار..."}

@app.get("/api/demo")
def demo():
    return paper.snapshot(state["last_price"])

@app.post("/api/demo/start")
def demo_start():
    state["running"]=True; paper.running=True
    return {"ok":True,"running":True}

@app.post("/api/demo/stop")
def demo_stop():
    state["running"]=False; paper.running=False
    return {"ok":True,"running":False}

@app.post("/api/demo/reset")
def demo_reset():
    paper.reset(); return paper.snapshot(state["last_price"])

@app.post("/api/demo/close")
def demo_close():
    ok=paper.close(state["last_price"],"MANUAL")
    return {"ok":ok,**paper.snapshot(state["last_price"])}

@app.post("/api/demo/settings")
def demo_settings(p:dict):
    for key in ("trade_usd","tp_pct","sl_pct"):
        if key in p:
            v=float(p[key])
            if key=="trade_usd": paper.trade_usd=max(1,v)
            if key=="tp_pct": paper.tp_pct=max(.05,v)
            if key=="sl_pct": paper.sl_pct=max(.05,v)
    return paper.snapshot(state["last_price"])

@app.post("/api/backtest")
async def backtest(file:UploadFile=File(...)):
    raw=await file.read()
    try:
        text=raw.decode("utf-8-sig")
        rows=list(csv.DictReader(io.StringIO(text)))
        cs=[]
        for r in rows:
            cs.append({"time":float(r.get("time",r.get("timestamp",len(cs)))),
                       "open":float(r["open"]),"high":float(r["high"]),
                       "low":float(r["low"]),"close":float(r["close"]),
                       "volume":float(r.get("volume",0))})
        if len(cs)<60: raise ValueError("حداقل 60 کندل لازم است")
        return run_backtest(cs,settings.demo_balance,settings.trade_usd,settings.fee_pct,settings.tp_pct,settings.sl_pct)
    except Exception as e:
        raise HTTPException(400,str(e))

async def collector():
    while True:
        try:
            raw=client.trades(settings.symbol,1000)
            cs=candles(raw)
            if cs:
                state["candles"]=cs
                state["last_price"]=cs[-1]["close"]
                state["last_analysis"]=analyze(cs)
                state["market_ok"]=True
                state["error"]=""
                state["last_update"]=time.strftime("%Y-%m-%d %H:%M:%S")
                if state["running"]:
                    a=state["last_analysis"]
                    paper.tick(state["last_price"],a.get("signal","HOLD"),a.get("confidence",0))
        except Exception as e:
            state["market_ok"]=False
            state["error"]=str(e)
        await asyncio.sleep(settings.interval)

@app.on_event("startup")
async def startup():
    state["running"]=settings.demo_start
    paper.running=state["running"]
    asyncio.create_task(collector())
