import pandas as pd

def analyze(candles: pd.DataFrame):
    if candles is None or len(candles) < 55:
        return {
            "signal": "HOLD",
            "confidence": 0,
            "reason": "Not enough 1-minute candles for EMA20/EMA50 + RSI14",
            "candles": 0 if candles is None else len(candles),
        }

    c = candles.copy()
    c["ema20"] = c["close"].ewm(span=20, adjust=False).mean()
    c["ema50"] = c["close"].ewm(span=50, adjust=False).mean()

    delta = c["close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, pd.NA)
    c["rsi14"] = 100 - (100 / (1 + rs))

    c["vol_ma20"] = c["volume"].rolling(20).mean()
    last = c.iloc[-1]

    price = float(last["close"])
    ema20 = float(last["ema20"])
    ema50 = float(last["ema50"])
    rsi = float(last["rsi14"]) if pd.notna(last["rsi14"]) else 50.0
    vol = float(last["volume"])
    vol_ma = float(last["vol_ma20"]) if pd.notna(last["vol_ma20"]) else 0.0
    vol_ratio = (vol / vol_ma) if vol_ma > 0 else 1.0

    score = 0
    reasons = []

    if ema20 > ema50:
        score += 1
        reasons.append("EMA20 above EMA50")
    elif ema20 < ema50:
        score -= 1
        reasons.append("EMA20 below EMA50")

    if rsi >= 52 and rsi <= 70:
        score += 1
        reasons.append("RSI supports bullish momentum")
    elif rsi <= 48 and rsi >= 30:
        score -= 1
        reasons.append("RSI supports bearish momentum")

    if vol_ratio >= 1.05:
        score += 1 if score >= 0 else -1
        reasons.append("volume confirmation")

    if score >= 2:
        signal = "BUY"
        confidence = min(95, 55 + score * 12)
    elif score <= -2:
        signal = "SELL"
        confidence = min(95, 55 + abs(score) * 12)
    else:
        signal = "HOLD"
        confidence = 50

    return {
        "signal": signal,
        "confidence": confidence,
        "price": round(price, 8),
        "rsi": round(rsi, 2),
        "ema20": round(ema20, 8),
        "ema50": round(ema50, 8),
        "volume": round(vol, 8),
        "volume_ratio": round(vol_ratio, 3),
        "candles": len(c),
        "reason": "; ".join(reasons) or "No strong confirmation",
    }
