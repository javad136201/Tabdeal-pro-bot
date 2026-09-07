
from decimal import Decimal
from . import tabdeal
from .config import settings

def preflight():
    if not settings.api_key or not settings.api_secret:return {'ok':False,'reason':'کلید API تنظیم نشده'}
    acct=tabdeal.account();return {'ok':True,'canTrade':acct.get('canTrade'),'canWithdraw':acct.get('canWithdraw'),'accountType':acct.get('accountType'),'balances':tabdeal.balance_map(acct)}

def market_buy(symbol,quote_amount):
    if not settings.live_enabled:raise RuntimeError('LIVE_TRADING_ENABLED=false')
    info=tabdeal.exchange_info(symbol); price=float(tabdeal.recent_trades(symbol,5)[-1]['price']); qty=tabdeal.norm_qty(float(quote_amount)/price,info)
    if qty<=0:raise RuntimeError('quantity became zero')
    return tabdeal.new_market_order(symbol,'BUY',format(qty,'f'))

def market_sell_all(symbol):
    if not settings.live_enabled:raise RuntimeError('LIVE_TRADING_ENABLED=false')
    info=tabdeal.exchange_info(symbol); base=info.get('baseAsset'); acct=tabdeal.account(); bal=tabdeal.balance_map(acct).get(base,{}).get('free',0); qty=tabdeal.norm_qty(bal,info)
    if qty<=0:raise RuntimeError('no free base balance to sell')
    return tabdeal.new_market_order(symbol,'SELL',format(qty,'f'))

def oco_for_long(symbol,qty,entry,tp_pct,sl_pct):
    info=tabdeal.exchange_info(symbol)
    tp=tabdeal.norm_price(entry*(1+tp_pct/100),info); stop=tabdeal.norm_price(entry*(1-sl_pct/100),info); stop_limit=tabdeal.norm_price(float(stop)*0.999,info)
    q=tabdeal.norm_qty(qty,info)
    return tabdeal.new_oco_sell(symbol,format(q,'f'),format(tp,'f'),format(stop,'f'),format(stop_limit,'f'),'bot_'+str(int(entry))+'_')
