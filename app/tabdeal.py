
import time, hmac, hashlib
from urllib.parse import urlencode
from decimal import Decimal, ROUND_DOWN
import requests
from .config import settings
BASE='https://api1.tabdeal.org'

def _variants(symbol): return [symbol.upper(),symbol.replace('_','').upper()]

def public_get(path,params=None):
    r=requests.get(BASE+path,params=params or {},timeout=12); r.raise_for_status(); return r.json()

def recent_trades(symbol,limit=500):
    last=None
    for s in _variants(symbol):
        try:
            d=public_get('/r/api/v1/trades',{'symbol':s,'limit':limit})
            if isinstance(d,list): return d
            if isinstance(d,dict):
                for k in ('data','results','trades'):
                    if isinstance(d.get(k),list): return d[k]
                return [d]
        except Exception as e: last=e
    raise RuntimeError(f'Tabdeal market request failed: {last}')

def exchange_info(symbol):
    for s in _variants(symbol):
        d=public_get('/r/api/v1/exchangeInfo',{'symbol':s})
        if isinstance(d,list) and d: return d[0]
        if isinstance(d,dict):
            if isinstance(d.get('symbols'),list) and d['symbols']: return d['symbols'][0]
            if d.get('symbol'): return d
    raise RuntimeError('exchangeInfo not found')

def _signed(method,path,params):
    if not settings.api_key or not settings.api_secret:
        raise RuntimeError('API key/secret are not configured')
    p=dict(params); p['timestamp']=int(time.time()*1000)
    query=urlencode(p)
    p['signature']=hmac.new(settings.api_secret.encode(),query.encode(),hashlib.sha256).hexdigest()
    headers={'X-MBX-APIKEY':settings.api_key}
    r=requests.request(method,BASE+path,params=p,headers=headers,timeout=15)
    r.raise_for_status(); return r.json()

def account(): return _signed('GET','/r/api/v1/account',{})
def open_orders(symbol): return _signed('GET','/r/api/v1/openOrders',{'symbol':symbol})
def get_order(symbol,order_id=None,client_order_id=None):
    p={'symbol':symbol}
    if order_id is not None: p['orderId']=order_id
    elif client_order_id: p['origClientOrderId']=client_order_id
    else: raise ValueError('order id required')
    return _signed('GET','/r/api/v1/order',p)
def new_market_order(symbol,side,quantity,client_order_id=None):
    p={'symbol':symbol,'side':side,'type':'MARKET','quantity':quantity}
    if client_order_id: p['newClientOrderId']=client_order_id
    return _signed('POST','/api/v1/order',p)
def new_oco_sell(symbol,quantity,price,stop_price,stop_limit_price,client_id_prefix):
    p={'symbol':symbol,'side':'SELL','quantity':quantity,'price':price,'stop_price':stop_price,'stop_limit_price':stop_limit_price,
       'list_client_order_id':client_id_prefix+'o','limit_client_order_id':client_id_prefix+'l','stop_client_order_id':client_id_prefix+'s'}
    return _signed('POST','/api/v1/order/oco',p)
def cancel_order(symbol,order_id): return _signed('DELETE','/api/v1/order',{'symbol':symbol,'orderId':order_id})

def balance_map(acct):
    return {b.get('asset'):{'free':float(b.get('free',0)),'freeze':float(b.get('freeze',0))} for b in acct.get('balances',[]) if isinstance(b,dict)}

def filters(info): return {f.get('filterType'):f for f in info.get('filters',[]) if isinstance(f,dict)}

def floor_step(value,step):
    v=Decimal(str(value)); s=Decimal(str(step))
    return (v/s).to_integral_value(rounding=ROUND_DOWN)*s

def norm_qty(value,info):
    fs=filters(info); f=fs.get('MARKET_LOT_SIZE') or fs.get('LOT_SIZE')
    if not f: return Decimal(str(value))
    q=floor_step(value,f.get('stepSize','1'))
    if q<Decimal(str(f.get('minQty','0'))): raise ValueError('quantity below exchange minimum')
    maxq=f.get('maxQty')
    if maxq and q>Decimal(str(maxq)): q=Decimal(str(maxq))
    return q

def norm_price(value,info):
    fs=filters(info); f=fs.get('PRICE_FILTER')
    if not f:return Decimal(str(value))
    p=floor_step(value,f.get('tickSize','1'))
    if p<Decimal(str(f.get('minPrice','0'))): raise ValueError('price below exchange minimum')
    return p
