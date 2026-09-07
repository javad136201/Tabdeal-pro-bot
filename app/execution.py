
import uuid,math
from . import tabdeal
class LiveExecutor:
 def __init__(self,s): self.s=s
 def preflight(self):
  a=tabdeal.account(self.s.api_key,self.s.api_secret);return {'ok':True,'canTrade':a.get('canTrade'),'canWithdraw':a.get('canWithdraw'),'permissions':a.get('permissions',[]),'balances':a.get('balances',[])}
 def normalize(self,symbol,qty):
  x=tabdeal.exchange_info(symbol); raw=x.get('symbols',[{}])[0] if isinstance(x,dict) and x.get('symbols') else x; step=mn=None
  for f in raw.get('filters',[]) if isinstance(raw,dict) else []:
   if (f.get('filterType') or f.get('type'))=='LOT_SIZE': step=float(f.get('stepSize') or 0); mn=float(f.get('minQty') or 0)
  if step: qty=math.floor(qty/step)*step
  if mn and qty<mn: raise ValueError(f'quantity below minimum {mn}')
  return f'{qty:.12f}'.rstrip('0').rstrip('.')
 def buy_quote(self,symbol,quote):
  ask=float(tabdeal.depth(symbol,5)['asks'][0][0]); q=self.normalize(symbol,quote/ask); return tabdeal.new_market_order(symbol,'BUY',q,self.s.api_key,self.s.api_secret,'bot_'+uuid.uuid4().hex[:20])
 def sell_base(self,symbol,qty):
  q=self.normalize(symbol,qty); return tabdeal.new_market_order(symbol,'SELL',q,self.s.api_key,self.s.api_secret,'bot_'+uuid.uuid4().hex[:20])
