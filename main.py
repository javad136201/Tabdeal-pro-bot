from fastapi import FastAPI,UploadFile,File
from fastapi.responses import FileResponse
from .config import settings
from .tabdeal import recent_trades
from .data import trades_to_1m,csv_ohlcv
from .storage import Store
from .strategy import analyze
from .paper import Paper
from .auto import Auto
from .backtest import run

app=FastAPI(title='Tabdeal Pro 4.1.1',version='4.1.1')
store=Store(settings.db)
demo=Paper('DEMO',settings.start,settings.order,settings.fee,store,settings)
forward=Paper('FORWARD',settings.start,settings.order,settings.fee,store,settings)

def refresh_market():
    raw=recent_trades(settings.symbol,settings.bootstrap)
    df=trades_to_1m(raw)
    store.save(settings.symbol,'1m',df)
    return df

def get_a():
    c=store.load(settings.symbol,2000)
    if len(c)<120:
        try: c=refresh_market() if len(c)<120 else c
        except Exception as e:
            return {'ready':False,'signal':'HOLD','confidence':0,'price':None,'reason':f'اتصال بازار: {e}'}
    return analyze(c,settings.profile,settings.min_confidence)

def cycle():
    try:
        refresh_market()
    except Exception as e:
        # keep old candles if market temporarily unavailable
        pass
    return get_a()

demo_auto=Auto('DEMO',cycle,demo,settings.market_poll)
forward_auto=Auto('FORWARD',cycle,forward,settings.market_poll)
try: refresh_market()
except Exception: pass
if settings.auto_demo: demo_auto.start()
if settings.auto_forward: forward_auto.start()

@app.get('/')
def root(): return FileResponse('app/static/index.html')

@app.get('/health')
def health(): return {'ok':True,'version':'4.1.1','demo_auto':demo_auto.running,'forward_auto':forward_auto.running,'demo_error':demo_auto.error,'forward_error':forward_auto.error}

@app.get('/api/status')
def status():
    try: stored=len(store.load(settings.symbol,2000))
    except Exception: stored=0
    return {'ok':True,'version':'4.1.1','symbol':settings.symbol,'base_asset':settings.symbol.split('_')[0],'quote_asset':'USDT','display_currency':'USD','demo_auto':demo_auto.running,'forward_auto':forward_auto.running,'live_locked':True,'stored_1m':stored,'profile':settings.profile,'min_confidence':settings.min_confidence,'market_poll_seconds':settings.market_poll}

@app.get('/api/candles')
def candles():
    try:
        c=store.load(settings.symbol,400)
        return {'ok':True,'symbol':settings.symbol,'interval':'1m','candles':[{'time':i.isoformat(),'open':float(r.open),'high':float(r.high),'low':float(r.low),'close':float(r.close),'volume':float(r.volume)} for i,r in c.iterrows()]}
    except Exception as e: return {'ok':False,'symbol':settings.symbol,'interval':'1m','candles':[],'error':str(e)}

@app.get('/api/analysis')
def analysis():
    try:return get_a()
    except Exception as e:return {'ready':False,'signal':'HOLD','confidence':0,'reason':f'خطای تحلیل: {e}'}

@app.get('/api/demo')
def demo_state(): return demo.snapshot()
@app.post('/api/demo/tick')
def demo_tick(): a=cycle(); return {'analysis':a,'state':demo.tick(a)}
@app.post('/api/demo/start')
def demo_start(): demo_auto.start(); return {'ok':True,'running':demo_auto.running}
@app.post('/api/demo/stop')
def demo_stop(): demo_auto.stop(); return {'ok':True,'running':demo_auto.running}
@app.post('/api/demo/reset')
def demo_reset(): demo.reset(); return demo.snapshot()
@app.post('/api/demo/manual-close')
def demo_close(): return demo.manual_close()

@app.get('/api/forward')
def forward_state(): return {'runner':{'running':forward_auto.running,'error':forward_auto.error},'state':forward.snapshot()}
@app.post('/api/forward/start')
def fstart(): forward_auto.start(); return {'ok':True,'running':forward_auto.running}
@app.post('/api/forward/stop')
def fstop(): forward_auto.stop(); return {'ok':True,'running':forward_auto.running}
@app.post('/api/forward/manual-close')
def fclose(): return forward.manual_close()
@app.post('/api/forward/reset')
def freset(): forward.reset(); return forward.snapshot()

@app.post('/api/settings')
def update_settings(payload:dict):
    # Runtime-safe settings. Live trading remains locked.
    numeric={'order_usd':'order','min_confidence':'min_conf','atr_stop_multiplier':'atr_mult','reward_risk':'rr','trailing_pct':'trail','cooldown_seconds':'cooldown','max_daily_loss_pct':'daily_loss','max_trades_per_day':'max_day'}
    for k,attr in numeric.items():
        if k in payload:
            v=float(payload[k])
            if k in ('cooldown_seconds','max_trades_per_day'): v=int(v)
            if k=='order_usd' and v<=0: raise ValueError('مبلغ معامله باید بزرگتر از صفر باشد')
            setattr(settings,attr,v)
    if 'profile' in payload:
        profile=str(payload['profile']).upper()
        if profile not in ('CONSERVATIVE','BALANCED','ACTIVE'): raise ValueError('پروفایل نامعتبر است')
        settings.profile=profile
    settings.min_confidence=float(settings.min_conf)
    settings.order_usd=float(settings.order)
    settings.cooldown_seconds=int(settings.cooldown)
    settings.max_daily_loss_pct=float(settings.daily_loss)
    settings.max_trades_per_day=int(settings.max_day)
    settings.atr_mult=float(settings.atr_mult);settings.rr=float(settings.rr);settings.trailing_pct=float(settings.trail)
    demo.order=settings.order; demo.cfg=settings
    forward.order=settings.order; forward.cfg=settings
    return {'ok':True,'profile':settings.profile,'order_usd':settings.order,'min_confidence':settings.min_confidence,'cooldown_seconds':settings.cooldown}

@app.post('/api/backtest/upload')
async def bt(file:UploadFile=File(...)):
    try:return run(csv_ohlcv(await file.read()),settings.start,settings.order,settings.fee,settings.profile,settings.min_confidence)
    except Exception as e:return {'ok':False,'error':str(e)}

@app.get('/api/live/preflight')
def live(): return {'ok':False,'locked':True,'message':'معامله واقعی عمداً در این نسخه قفل است؛ ابتدا Demo و Forward را کامل تست می‌کنیم.'}
