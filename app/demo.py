
from dataclasses import dataclass, asdict
from threading import Lock
from pathlib import Path
import json

@dataclass
class DemoState:
    quote_balance: float
    base_balance: float = 0.0
    entry_price: float = 0.0
    take_profit: float = 0.0
    stop_loss: float = 0.0
    total_fees: float = 0.0
    realized_pnl: float = 0.0
    trades: list = None
    last_signal: str = "HOLD"
    last_price: float = 0.0
    halted: bool = False

    def __post_init__(self):
        if self.trades is None:
            self.trades = []

class DemoEngine:
    def __init__(self, start_quote=1000.0, trade_quote=50.0, fee_rate=0.001, state_file=None):
        self.start_quote = start_quote
        self.trade_quote = trade_quote
        self.fee_rate = fee_rate
        self.state_file = state_file
        self._lock = Lock()
        self.state = DemoState(start_quote)
        self._load()

    def _save(self):
        if not self.state_file:
            return
        try:
            p = Path(self.state_file)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(asdict(self.state)), encoding='utf-8')
        except Exception:
            pass

    def _load(self):
        if not self.state_file:
            return
        try:
            p = Path(self.state_file)
            if not p.exists(): return
            d = json.loads(p.read_text(encoding='utf-8'))
            allowed = {k: d[k] for k in DemoState.__dataclass_fields__ if k in d}
            self.state = DemoState(**allowed)
        except Exception:
            self.state = DemoState(self.start_quote)

    def reset(self):
        with self._lock:
            self.state = DemoState(self.start_quote)
            self._save()
            return self.snapshot()

    def halt(self):
        with self._lock:
            self.state.halted = True
            self._save()

    def resume(self):
        with self._lock:
            self.state.halted = False
            self._save()

    def configure_risk(self, take_profit_pct=None, stop_loss_pct=None):
        with self._lock:
            if self.state.base_balance <= 0 or self.state.entry_price <= 0:
                return self.snapshot()
            if take_profit_pct is not None:
                tp = max(0.0, float(take_profit_pct))
                self.state.take_profit = self.state.entry_price * (1 + tp/100.0)
            if stop_loss_pct is not None:
                sl = max(0.0, float(stop_loss_pct))
                self.state.stop_loss = self.state.entry_price * (1 - sl/100.0)
            self._save()
            return self.snapshot()

    def _open(self, price, take_profit_pct=None, stop_loss_pct=None, reason='SIGNAL'):
        spend = min(self.trade_quote, self.state.quote_balance)
        if spend <= 0: return
        fee = spend * self.fee_rate
        qty = (spend - fee) / price
        self.state.quote_balance -= spend
        self.state.base_balance += qty
        self.state.entry_price = price
        tp_pct = 2.0 if take_profit_pct is None else max(0.0, float(take_profit_pct))
        sl_pct = 1.0 if stop_loss_pct is None else max(0.0, float(stop_loss_pct))
        self.state.take_profit = price * (1 + tp_pct/100.0)
        self.state.stop_loss = price * (1 - sl_pct/100.0)
        self.state.total_fees += fee
        self.state.trades.append({
            'side':'BUY','price':price,'qty':qty,'quote':spend,'fee':fee,'pnl':0.0,
            'reason':reason,'take_profit':self.state.take_profit,'stop_loss':self.state.stop_loss
        })

    def _close(self, price, reason='SIGNAL'):
        qty = self.state.base_balance
        if qty <= 0: return None
        gross = qty * price
        fee = gross * self.fee_rate
        net = gross - fee
        cost = qty * self.state.entry_price
        pnl = net - cost
        self.state.quote_balance += net
        self.state.base_balance = 0.0
        self.state.entry_price = 0.0
        self.state.take_profit = 0.0
        self.state.stop_loss = 0.0
        self.state.total_fees += fee
        self.state.realized_pnl += pnl
        self.state.trades.append({
            'side':'SELL','price':price,'qty':qty,'quote':gross,'fee':fee,'pnl':pnl,'reason':reason
        })
        return pnl

    def close_manual(self, price):
        with self._lock:
            if price <= 0 or self.state.base_balance <= 0:
                return self.snapshot()
            self._close(price, 'MANUAL')
            self._save()
            return self.snapshot()

    def tick(self, analysis, take_profit_pct=None, stop_loss_pct=None):
        with self._lock:
            signal = analysis.get('signal','HOLD')
            price = float(analysis.get('price') or 0)
            self.state.last_signal = signal
            if price <= 0:
                return self.snapshot()
            self.state.last_price = price

            if self.state.halted:
                self._save()
                return self.snapshot()

            # Protective exits always have priority over strategy signal.
            if self.state.base_balance > 0:
                if self.state.take_profit > 0 and price >= self.state.take_profit:
                    self._close(price, 'TAKE_PROFIT')
                elif self.state.stop_loss > 0 and price <= self.state.stop_loss:
                    self._close(price, 'STOP_LOSS')
                elif signal == 'SELL':
                    self._close(price, 'SIGNAL')
            elif signal == 'BUY':
                self._open(price, take_profit_pct, stop_loss_pct, 'SIGNAL')

            self._save()
            return self.snapshot()

    def snapshot(self):
        s = self.state
        equity = s.quote_balance + (s.base_balance * s.last_price)
        unrealized = 0.0
        if s.base_balance > 0 and s.entry_price > 0 and s.last_price > 0:
            unrealized = (s.last_price - s.entry_price) * s.base_balance
        return {
            **asdict(s),
            'equity': round(equity,8),
            'unrealized_pnl': round(unrealized,8),
            'total_pnl': round(equity-self.start_quote,8),
            'position': 'LONG' if s.base_balance > 0 else 'FLAT',
            'trades_count': len(s.trades),
            'risk': {
                'take_profit_price': round(s.take_profit,8) if s.take_profit else None,
                'stop_loss_price': round(s.stop_loss,8) if s.stop_loss else None,
            }
        }
