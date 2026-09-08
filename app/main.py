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
app=FastAPI(title='Tabdeal Pro 4.1',version='4.1.0')
store=Store(settings.db)
def get_a():return analyze(store.load(settings.symbol),settings.profile,settings.min_confidence)
demo=Paper('DEMO',settings.start,settings.order,settings.fee,store,settings);forward=Paper('FORWARD',settings.start,settings.order,settings.fee,store,settings)
demo_auto=Auto('DEMO',get_a,demo,settings.market_poll);forward_auto=Auto('FORWARD',get_a,forward,settings.market_poll)
def bootstrap():
    try:store.save(settings.symbol,'1m',trades_to_1m(recent_trades(settings.symbol,settings.bootstrap)))
    except Exception:pass
bootstrap()
if settings.auto_demo:demo_auto.start()
if settings.auto_forward:forward_auto.start()
@app.get('/')
def root():return FileResponse('app/static/index.html')
@app.get('/health')
def health():return {'ok':True,'version':'4.1.0','demo_auto':demo_auto.running,'forward_auto':forward_auto.running}
@app.get('/api/status')
def status():return {'version':'4.1.0','symbol':settings.symbol,'base_asset':settings.symbol.split('_')[0],'quote_asset':'USDT','display_currency':'USD','demo_auto':demo_auto.running,'forward_auto':forward_auto.running,'live_locked':True}
@app.get('/api/candles')
def candles():
 c=store.load(settings.symbol,300)
 return {'symbol':settings.symbol,'interval':'1m','candles':[{'time':i.isoformat(),'open':r.open,'high':r.high,'low':r.low,'close':r.close,'volume':r.volume} for i,r in c.iterrows()]}
@app.get('/api/analysis')
def analysis():return get_a()
@app.get('/api/demo')
def demo_state():return demo.snapshot()
@app.post('/api/demo/tick')
def demo_tick():a=get_a();return {'analysis':a,'state':demo.tick(a)}
@app.post('/api/demo/start')
def demo_start():demo_auto.start();return demo_auto.running
@app.post('/api/demo/stop')
def demo_stop():demo_auto.stop();return demo_auto.running
@app.post('/api/demo/reset')
def demo_reset():demo.reset();return demo.snapshot()
@app.post('/api/demo/manual-close')
def demo_close():return demo.manual_close()
@app.get('/api/forward')
def forward_state():return {'runner':{'running':forward_auto.running,'error':forward_auto.error},'state':forward.snapshot()}
@app.post('/api/forward/start')
def fstart():forward_auto.start();return forward_auto.running
@app.post('/api/forward/stop')
def fstop():forward_auto.stop();return forward_auto.running
@app.post('/api/forward/manual-close')
def fclose():return forward.manual_close()
@app.post('/api/forward/reset')
def freset():forward.reset();return forward.snapshot()
@app.post('/api/backtest/upload')
async def bt(file:UploadFile=File(...)):
 try:return run(csv_ohlcv(await file.read()),settings.start,settings.order,settings.fee,settings.profile,settings.min_confidence)
 except Exception as e:return {'ok':False,'error':str(e)}
@app.get('/api/live/preflight')
def live():return {'ok':False,'locked':True,'message':'Live trading is intentionally locked in v4.1'}
