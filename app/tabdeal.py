import requests

class Tabdeal:
    def __init__(self, base_url):
        self.base = base_url.rstrip("/")
        self.s = requests.Session()

    @staticmethod
    def variants(symbol):
        return list(dict.fromkeys([symbol, symbol.replace("_",""), symbol.replace("-","")]))

    def _get(self, path, params):
        r = self.s.get(self.base + path, params=params, timeout=12)
        r.raise_for_status()
        return r.json()

    def trades(self, symbol, limit=1000):
        last = None
        for sym in self.variants(symbol):
            try:
                data = self._get("/r/api/v1/trades", {"symbol": sym, "limit": limit})
                if isinstance(data, list):
                    return [x for x in data if isinstance(x, dict)]
                if isinstance(data, dict):
                    for k in ("data","trades","results"):
                        if isinstance(data.get(k), list):
                            return [x for x in data[k] if isinstance(x,dict)]
            except Exception as e:
                last = e
        raise RuntimeError(f"Tabdeal trades failed: {last}")

    def exchange_info(self, symbol):
        for sym in self.variants(symbol):
            try:
                data = self._get("/r/api/v1/exchangeInfo", {"symbol": sym})
                if isinstance(data, list) and data:
                    return data[0]
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
        return {}

    def ping(self):
        r = self.s.get(self.base + "/r/api/v1/ping", timeout=8)
        r.raise_for_status()
        return True
