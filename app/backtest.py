import pandas as pd
from .strategy import analyze

def run_backtest(candles: pd.DataFrame, starting_quote=1000.0, fee_rate=0.001):
    if candles is None or len(candles) < 60:
        return {"ok": False, "error": "At least 60 candles are required"}

    cash = float(starting_quote)
    qty = 0.0
    entry = 0.0
    trades = []

    # Walk forward; strategy uses only candles available up to each step.
    for i in range(55, len(candles)):
        window = candles.iloc[:i+1]
        a = analyze(window)
        price = float(window["close"].iloc[-1])
        if a["signal"] == "BUY" and qty == 0:
            spend = cash
            fee = spend * fee_rate
            qty = (spend - fee) / price
            cash = 0.0
            entry = price
            trades.append({"side":"BUY","price":price,"qty":qty})
        elif a["signal"] == "SELL" and qty > 0:
            gross = qty * price
            fee = gross * fee_rate
            cash = gross - fee
            pnl = cash - (qty * entry)
            trades.append({"side":"SELL","price":price,"qty":qty,"pnl":pnl})
            qty = 0.0
            entry = 0.0

    final_price = float(candles["close"].iloc[-1])
    equity = cash + qty * final_price
    return {
        "ok": True,
        "starting_quote": starting_quote,
        "final_equity": round(equity, 8),
        "pnl": round(equity - starting_quote, 8),
        "return_pct": round((equity / starting_quote - 1) * 100, 4),
        "trades": trades,
        "trades_count": len(trades),
        "note": "Backtest uses 1-minute candles built from available trades; it is not a substitute for a verified historical OHLCV dataset."
    }
