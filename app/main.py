
import time, threading
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from .config import settings
from .tabdeal import recent_trades, account, depth
from .data import trades_to_candles, csv_to_candles
from .strategy import analyze
from .demo import DemoEngine
from .execution import LiveExecutor
from .risk import Risk
from .backtest import run

app=FastAPI(title='Tabdeal Pro Final',version='2.1.0')
demo=DemoEngine(settings.demo_start_quote,settings.trade_quote,settings.fee_rate,settings.state_file)
live=LiveExecutor(settings)
risk=Risk(settings.max_daily_loss,settings.max_trades_per_day,settings.cooldown_seconds)

class RiskRequest(BaseModel):
    take_profit_pct: float = 2.0
    stop_loss_pct: float = 1.0

class ModeAction(BaseModel):
    action: str

def get_a():
    return analyze(trades_to_candles(recent_trades(settings.symbol,settings.market_limit),settings.candle_minutes))

def base_asset():
    return settings.symbol.replace('_','').upper().split('USDT')[0].split('IRT')[0]

@app.get('/')
def root(): return FileResponse('app/static/index.html')
@app.get('/health')
def health(): return {'ok':True,'version':'2.1.0'}
@app.get('/api/status')
def status():
    return {'mode':settings.mode,'symbol':settings.symbol,'version':'2.1.0','live_enabled':settings.live_enabled,'auto_trading':settings.auto_trading,'emergency_stop':risk.stop}
@app.get('/api/analysis')
def analysis():
    try: return get_a()
    except Exception as e: return {'signal':'HOLD','confidence':0,'error':str(e)}

@app.get('/api/position')
def position():
    if settings.mode == 'DEMO':
        return {'mode':'DEMO', **demo.snapshot()}
    return {'mode':'LIVE', 'symbol':settings.symbol, 'warning':'Live position shown only after API preflight'}

@app.get('/api/demo/state')
def ds(): return demo.snapshot()
@app.post('/api/demo/settings')
def demo_settings(body: RiskRequest):
    return demo.configure_risk(body.take_profit_pct, body.stop_loss_pct)
@app.post('/api/demo/tick')
def dt():
    a=get_a(); return {'ok':True,'analysis':a,'demo':demo.tick(a)}
@app.post('/api/demo/close')
def dc():
    a=get_a(); return {'ok':True,'demo':demo.close_manual(float(a.get('price') or 0))}
@app.post('/api/demo/reset')
def dr(): return demo.reset()
@app.post('/api/demo/stop')
def dstop(): demo.halt(); return demo.snapshot()
@app.post('/api/demo/resume')
def dres(): demo.resume(); return demo.snapshot()

@app.get('/api/backtest')
def bt():
    return run(trades_to_candles(recent_trades(settings.symbol,settings.market_limit),settings.candle_minutes),settings.demo_start_quote,settings.fee_rate,settings.trade_quote)
@app.post('/api/backtest/csv')
async def btc(file:UploadFile=File(...)):
    p='/tmp/bt.csv'; open(p,'wb').write(await file.read()); return run(csv_to_candles(p),settings.demo_start_quote,settings.fee_rate,settings.trade_quote)

@app.get('/api/live/preflight')
def pf():
    if not settings.api_key or not settings.api_secret: return {'ok':False,'error':'API credentials missing in Railway Variables'}
    try: return live.preflight()
    except Exception as e: return {'ok':False,'error':str(e)}

def guard():
    if not settings.live_enabled: raise HTTPException(403,'LIVE_TRADING_ENABLED=false')
    if settings.live_confirmation!='I_UNDERSTAND_LIVE_RISK': raise HTTPException(403,'LIVE_CONFIRMATION missing')
    if risk.stop: raise HTTPException(403,'Emergency stop active')
    if not settings.api_key or not settings.api_secret: raise HTTPException(403,'API credentials missing')

def live_asset_balance():
    a=account(settings.api_key,settings.api_secret)
    asset=base_asset()
    for b in a.get('balances',[]):
        if str(b.get('asset','')).upper()==asset:
            return float(b.get('free',b.get('available',0)) or 0)
    return 0.0

@app.post('/api/live/buy')
def lb():
    guard(); a=get_a()
    if a.get('signal')!='BUY': return {'ok':False,'blocked':'signal_not_buy','analysis':a}
    ok,why=risk.allow(0)
    if not ok:return {'ok':False,'blocked':why}
    o=live.buy_quote(settings.symbol,settings.trade_quote); risk.record(); return {'ok':True,'analysis':a,'order':o}

@app.post('/api/live/close')
def lc():
    guard()
    qty=live_asset_balance()
    if qty<=0:return {'ok':False,'blocked':'NO_BASE_ASSET_POSITION'}
    o=live.sell_base(settings.symbol,qty)
    return {'ok':True,'order':o,'closed_quantity':qty}

@app.post('/api/live/stop')
def ls(): risk.stop=True; return {'ok':True,'emergency_stop':True}
@app.post('/api/live/resume')
def lr(): risk.stop=False; return {'ok':True,'emergency_stop':False}

def worker():
    while True:
        try:
            if settings.auto_trading and settings.mode=='DEMO': demo.tick(get_a())
        except Exception:
            pass
        time.sleep(15)
threading.Thread(target=worker,daemon=True).start()
