import time, hmac, hashlib, requests
from .config import settings

class TabdealClient:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent":"Tabdeal-Pro-Bot/1.0"})

    def public(self, path, params=None):
        r = self.s.get(settings.base_url + path, params=params, timeout=15)
        r.raise_for_status()
        return r.json()

    def signed(self, method, path, params=None):
        params = dict(params or {})
        params["timestamp"] = int(time.time()*1000)
        query = "&".join(f"{k}={params[k]}" for k in params)
        sig = hmac.new(settings.secret_key.encode(), query.encode(), hashlib.sha256).hexdigest()
        headers = {"X-MBX-APIKEY": getattr(settings, "api_key", "")}
        params["signature"] = sig
        r = self.s.request(method, settings.base_url + path, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        return r.json()

    def ping(self):
        return self.public("/r/api/v1/ping")

    def trades(self, symbol=None, limit=1000):
        return self.public("/r/api/v1/trades", {"symbol":symbol or settings.symbol,"limit":limit})

    def exchange_info(self, symbol=None):
        return self.public("/r/api/v1/exchangeInfo", {"symbol":symbol or settings.symbol})

    def account(self):
        return self.signed("GET","/r/api/v1/account")

    def market_order(self, side, quantity, symbol=None):
        return self.signed("POST","/api/v1/order", {
            "symbol":symbol or settings.symbol,
            "side":side,
            "type":"MARKET",
            "quantity":str(quantity)
        })
