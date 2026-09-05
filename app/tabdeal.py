import requests
class TabdealClient:
    def __init__(self,*a,**k):pass
    def recent_trades(self,symbol,limit=100):
        return requests.get('https://api1.tabdeal.org/r/api/v1/trades',params={'symbol':symbol,'limit':limit},timeout=10).json()
