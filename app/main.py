
from fastapi import FastAPI,UploadFile,File,HTTPException,Response,Cookie
from fastapi.responses import FileResponse
from pydantic import BaseModel,Field
import pandas as pd, time
from .config import settings
from .tabdeal import recent_trades
from .data import trades_to_candles,normalize_ohlcv_csv
from .strategy import analyze
from .paper import PaperEngine
from .backtest import run
from .forward import ForwardTester
from . import live
import hmac,hashlib,secrets
app=FastAPI(title='Tabdeal Pro',version='3.0.0')
paper=PaperEngine(settings.demo_start_quote,settings.demo_trade_quote,settings.fee_rate,settings.tp_pct,settings.sl_pct,settings.trailing_pct)

def market_raw():return recent_trades(settings.symbol,settings.market_limit)
def analysis_now():return analyze(trades_to_candles(market_raw()))
forward=ForwardTester(market_raw,lambda raw:analyze(trades_to_candles(raw)),settings.poll_seconds)

def session_ok(cookie):
    if not settings.dashboard_password:return False
    if not cookie:return False
    token,sep,sig=cookie.partition('.');
    expected=hmac.new(settings.dashboard_password.encode(),token.encode(),hashlib.sha256).hexdigest()
    return sep=='.' and hmac.compare_digest(sig,expected)

def require_session(cookie):
    if not session_ok(cookie):raise HTTPException(401,'برای عملیات واقعی ابتدا وارد پنل شوید.')

class Login(BaseModel): password:str
class Risk(BaseModel): tp:float=Field(ge=0,le=100);sl:float=Field(ge=0,le=100);trailing:float=Field(ge=0,le=50)
class Amount(BaseModel): quote:float=Field(gt=0,le=100000000)

@app.get('/')
def root():return FileResponse('app/static/index.html')
@app.get('/health')
def health():return {'ok':True,'version':'3.0.0'}
@app.get('/api/status')
def status():return {'mode':settings.mode,'symbol':settings.symbol,'version':'3.0.0','demo_enabled':settings.demo_enabled,'forward_enabled':settings.forward_enabled,'live_enabled':settings.live_enabled}
@app.post('/api/login')
def login(body:Login,response:Response):
    if not settings.dashboard_password or not secrets.compare_digest(body.password,settings.dashboard_password):raise HTTPException(401,'رمز نادرست است.')
    token=secrets.token_urlsafe(24);sig=hmac.new(settings.dashboard_password.encode(),token.encode(),hashlib.sha256).hexdigest();response.set_cookie('tp_session',token+'.'+sig,httponly=True,samesite='lax',secure=False,max_age=86400)
    return {'ok':True}
@app.post('/api/logout')
def logout(response:Response):response.delete_cookie('tp_session');return {'ok':True}
@app.get('/api/analysis')
def analysis():
    try:return analysis_now()
    except Exception as e:return {'signal':'HOLD','confidence':0,'error':str(e)}
@app.get('/api/demo/state')
def demo_state():return paper.snapshot()
@app.post('/api/demo/config')
def demo_config(r:Risk):return paper.configure(r.tp,r.sl,r.trailing)
@app.post('/api/demo/tick')
def demo_tick():return {'ok':True,'analysis':analysis_now(),'demo':paper.process(analysis_now())}
@app.post('/api/demo/manual-close')
def demo_close():return paper.manual_close()
@app.post('/api/demo/reset')
def demo_reset():return paper.reset()
@app.post('/api/forward/start')
def forward_start():forward.start();return forward.snapshot()
@app.post('/api/forward/stop')
def forward_stop():forward.stop();return forward.snapshot()
@app.post('/api/forward/tick')
def forward_tick():return forward.tick()
@app.post('/api/forward/reset')
def forward_reset():forward.stop();forward.reset();return forward.snapshot()
@app.get('/api/forward/state')
def forward_state():return forward.snapshot()
@app.post('/api/backtest/csv')
async def backtest_csv(file:UploadFile=File(...)):
    if not file.filename.lower().endswith('.csv'):raise HTTPException(400,'فقط CSV پذیرفته می‌شود.')
    data=await file.read()
    try:
        import io
        df=pd.read_csv(io.BytesIO(data));candles=normalize_ohlcv_csv(df);return run(candles,settings.demo_start_quote,settings.fee_rate,paper.tp,paper.sl)
    except Exception as e:raise HTTPException(400,str(e))
@app.get('/api/backtest/current')
def backtest_current():return run(trades_to_candles(market_raw()),settings.demo_start_quote,settings.fee_rate,paper.tp,paper.sl)
@app.get('/api/live/preflight')
def preflight(cookie=Cookie(default=None,alias='tp_session')):
    require_session(cookie);return live.preflight()
@app.post('/api/live/buy')
def live_buy(body:Amount,cookie=Cookie(default=None,alias='tp_session')):
    require_session(cookie)
    if not settings.live_enabled:raise HTTPException(403,'Live trading قفل است. LIVE_TRADING_ENABLED را فعال کنید.')
    try:
        result=live.market_buy(settings.symbol,body.quote);return {'ok':True,'order':result}
    except Exception as e:raise HTTPException(400,str(e))
@app.post('/api/live/sell-all')
def live_sell(cookie=Cookie(default=None,alias='tp_session')):
    require_session(cookie)
    try:return {'ok':True,'order':live.market_sell_all(settings.symbol)}
    except Exception as e:raise HTTPException(400,str(e))
