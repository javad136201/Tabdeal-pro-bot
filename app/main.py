import os
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .config import settings
from .tabdeal import TabdealClient
from .services.backtest import run_backtest

app=FastAPI(title="Tabdeal Pro Bot", version="1.0.0")
client=TabdealClient()
ROOT=Path(__file__).parent
state={"mode":settings.mode,"symbol":settings.symbol,"running":False,"signal":"WAIT","score":0,
       "price":None,"rsi":None,"ema20":None,"ema50":None,"macd":None,
       "trades_today":0,"last_error":None}

class BacktestRequest(BaseModel):
    csv_path:str
    initial_cash:float=10_000_000
    trade_amount:float=1_000_000
    fee_rate:float=settings.fee_rate
    stop_loss_pct:float=settings.stop_loss_pct
    take_profit_pct:float=settings.take_profit_pct
    rsi_buy:float=settings.rsi_buy
    rsi_sell:float=settings.rsi_sell
    min_score:int=settings.min_score

@app.get("/")
def dashboard():
    return FileResponse(ROOT/"static"/"index.html")

@app.get("/api/status")
def status():
    return state

@app.get("/api/market")
def market():
    try:
        t=client.trades(settings.symbol,100)
        return {"symbol":settings.symbol,"trades":t}
    except Exception as e:
        raise HTTPException(502,str(e))

@app.post("/api/mode/{mode}")
def set_mode(mode:str):
    mode=mode.upper()
    if mode not in ("BACKTEST","DEMO","LIVE"):
        raise HTTPException(400,"Invalid mode")
    if mode=="LIVE" and settings.mode!="LIVE":
        # Production should use an explicit Railway variable to enable LIVE.
        raise HTTPException(403,"LIVE is disabled. Set TRADING_MODE=LIVE in Railway after testing.")
    state["mode"]=mode
    return state

@app.post("/api/start")
def start():
    state["running"]=True
    return state

@app.post("/api/stop")
def stop():
    state["running"]=False
    return state

@app.post("/api/emergency-stop")
def emergency_stop():
    state["running"]=False
    state["signal"]="STOPPED"
    return state

@app.post("/api/backtest")
def backtest(req:BacktestRequest):
    p=Path(req.csv_path)
    if not p.exists(): raise HTTPException(404,"CSV file not found on server")
    df=pd.read_csv(p)
    df.columns=[c.lower() for c in df.columns]
    required={"open","high","low","close","volume"}
    if not required.issubset(df.columns):
        raise HTTPException(400,"CSV needs open, high, low, close, volume columns")
    return run_backtest(df,req.initial_cash,req.trade_amount,req.fee_rate,
                        req.stop_loss_pct,req.take_profit_pct,
                        req.rsi_buy,req.rsi_sell,req.min_score)
