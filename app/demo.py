from dataclasses import dataclass, asdict
from threading import Lock

@dataclass
class DemoState:
    quote_balance: float
    base_balance: float = 0.0
    entry_price: float = 0.0
    total_fees: float = 0.0
    realized_pnl: float = 0.0
    trades: list = None
    last_signal: str = "HOLD"
    last_price: float = 0.0

    def __post_init__(self):
        if self.trades is None:
            self.trades = []

class DemoEngine:
    def __init__(self, start_quote=1000.0, trade_quote=50.0, fee_rate=0.001):
        self.start_quote = start_quote
        self.trade_quote = trade_quote
        self.fee_rate = fee_rate
        self._lock = Lock()
        self.state = DemoState(start_quote)

    def reset(self):
        with self._lock:
            self.state = DemoState(self.start_quote)
            return self.snapshot()

    def tick(self, analysis):
        with self._lock:
            signal = analysis.get("signal", "HOLD")
            price = float(analysis.get("price") or 0)
            self.state.last_signal = signal
            if price <= 0:
                return self.snapshot()

            self.state.last_price = price

            # Enter only when flat.
            if signal == "BUY" and self.state.base_balance <= 0:
                spend = min(self.trade_quote, self.state.quote_balance)
                if spend > 0:
                    fee = spend * self.fee_rate
                    qty = (spend - fee) / price
                    self.state.quote_balance -= spend
                    self.state.base_balance += qty
                    self.state.entry_price = price
                    self.state.total_fees += fee
                    self.state.trades.append({
                        "side": "BUY", "price": price, "qty": qty,
                        "quote": spend, "fee": fee, "pnl": 0.0
                    })

            # Exit only when holding a position.
            elif signal == "SELL" and self.state.base_balance > 0:
                qty = self.state.base_balance
                gross = qty * price
                fee = gross * self.fee_rate
                net = gross - fee
                cost = qty * self.state.entry_price
                pnl = net - cost
                self.state.quote_balance += net
                self.state.base_balance = 0.0
                self.state.entry_price = 0.0
                self.state.total_fees += fee
                self.state.realized_pnl += pnl
                self.state.trades.append({
                    "side": "SELL", "price": price, "qty": qty,
                    "quote": gross, "fee": fee, "pnl": pnl
                })

            return self.snapshot()

    def snapshot(self):
        s = self.state
        equity = s.quote_balance + (s.base_balance * s.last_price)
        unrealized = 0.0
        if s.base_balance > 0 and s.entry_price > 0 and s.last_price > 0:
            unrealized = (s.last_price - s.entry_price) * s.base_balance
        return {
            **asdict(s),
            "equity": round(equity, 8),
            "unrealized_pnl": round(unrealized, 8),
            "total_pnl": round(equity - self.start_quote, 8),
            "position": "LONG" if s.base_balance > 0 else "FLAT",
            "trades_count": len(s.trades),
        }
