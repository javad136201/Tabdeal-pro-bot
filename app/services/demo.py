class DemoBroker:
    def __init__(self, cash=10_000_000):
        self.cash=float(cash); self.asset=0.0; self.entry=None; self.history=[]
    def buy(self, price, amount):
        if amount<=self.cash:
            self.asset=amount/price; self.cash-=amount; self.entry=price
            self.history.append({"side":"BUY","price":price,"amount":amount})
            return True
        return False
    def sell(self, price):
        if self.asset>0:
            amount=self.asset*price; self.cash+=amount
            self.history.append({"side":"SELL","price":price,"amount":amount})
            self.asset=0; self.entry=None; return True
        return False
    def equity(self, price):
        return self.cash+self.asset*price
