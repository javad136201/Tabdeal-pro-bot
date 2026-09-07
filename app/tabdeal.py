import hashlib,hmac,time,requests
from urllib.parse import urlencode
BASE="https://api1.tabdeal.org"
def variants(s): return [s.upper(),s.replace("_","").upper()]
def req(method,path,params=None,signed=False,key="",secret=""):
 p=dict(params or {});h={}
 if signed:
  if not key or not secret: raise RuntimeError("API credentials are not configured")
  p["timestamp"]=int(time.time()*1000);q=urlencode(p);p["signature"]=hmac.new(secret.encode(),q.encode(),hashlib.sha256).hexdigest();h["X-MBX-APIKEY"]=key
 r=requests.request(method,BASE+path,params=p,headers=h,timeout=12);r.raise_for_status();return r.json()
def recent_trades(symbol,limit=1000):
 err=None
 for s in variants(symbol):
  try:
   x=req("GET","/r/api/v1/trades",{"symbol":s,"limit":limit})
   if isinstance(x,list): return x
   if isinstance(x,dict):
    for k in ("data","results","trades"):
     if isinstance(x.get(k),list): return x[k]
    return [x]
  except Exception as e: err=e
 raise RuntimeError(f"Tabdeal trades request failed: {err}")
def depth(symbol,limit=20):
 for s in variants(symbol):
  try:return req("GET","/r/api/v1/depth",{"symbol":s,"limit":limit})
  except Exception:pass
 raise RuntimeError("Unable to read order book")
def exchange_info(symbol=None): return req("GET","/r/api/v1/exchangeInfo",{"symbol":symbol.replace("_","").upper()} if symbol else {})
def account(key,secret): return req("GET","/r/api/v1/account",signed=True,key=key,secret=secret)
def new_market_order(symbol,side,quantity,key,secret,client_id): return req("POST","/api/v1/order",{"symbol":symbol.replace("_","").upper(),"side":side,"type":"MARKET","quantity":str(quantity),"newClientOrderId":client_id},True,key,secret)
