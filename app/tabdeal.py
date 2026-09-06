import requests
BASE_URL="https://api1.tabdeal.org"
class TabdealClient:
    def __init__(self,api_key="",api_secret="",timeout=15):
        self.api_key=api_key; self.api_secret=api_secret; self.timeout=timeout
    def recent_trades(self,symbol,limit=500):
        last=None
        for s in (symbol.upper(),symbol.upper().replace("_","")):
            try:
                r=requests.get(f"{BASE_URL}/r/api/v1/trades",params={"symbol":s,"limit":min(int(limit),1000)},timeout=self.timeout)
                r.raise_for_status(); d=r.json()
                if isinstance(d,list): return d
                if isinstance(d,dict):
                    for k in ("data","results","trades"):
                        if isinstance(d.get(k),list): return d[k]
                raise ValueError("Unexpected trades response")
            except Exception as e: last=e
        raise RuntimeError(f"Tabdeal trades request failed: {last}")
