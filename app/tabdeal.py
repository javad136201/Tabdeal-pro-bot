import requests
BASE='https://api1.tabdeal.org'
def recent_trades(symbol,limit=1000):
    last=None
    for s in (symbol.upper(),symbol.replace('_','').upper()):
        try:
            r=requests.get(f'{BASE}/r/api/v1/trades',params={'symbol':s,'limit':limit},timeout=12);r.raise_for_status();d=r.json()
            if isinstance(d,list):return d
            if isinstance(d,dict):
                for k in ('data','results','trades'):
                    if isinstance(d.get(k),list):return d[k]
                return [d]
        except Exception as e:last=e
    raise RuntimeError(f'market request failed: {last}')
