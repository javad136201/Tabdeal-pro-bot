import pandas as pd


def _rsi(s, n=14):
    d = s.diff()
    gain = d.clip(lower=0).ewm(alpha=1/n, adjust=False).mean()
    loss = (-d.clip(upper=0)).ewm(alpha=1/n, adjust=False).mean()
    rs = gain / loss.replace(0, pd.NA)
    return 100 - (100 / (1 + rs))


def analyze(candles: pd.DataFrame, min_confidence=60):
    if candles is None or len(candles) < 60:
        return {
            "signal": "HOLD", "confidence": 0, "price": None,
            "rsi": None, "ema20": None, "ema50": None,
            "macd": None, "macd_signal": None, "atr": None,
            "volume_ratio": None, "trend": "UNKNOWN",
            "reason": "برای تحلیل پایدار حداقل ۶۰ کندل لازم است.",
            "candles": 0 if candles is None else len(candles)
        }

    c = candles.copy()
    c["ema20"] = c["close"].ewm(span=20, adjust=False).mean()
    c["ema50"] = c["close"].ewm(span=50, adjust=False).mean()
    c["rsi"] = _rsi(c["close"], 14)

    ema12 = c["close"].ewm(span=12, adjust=False).mean()
    ema26 = c["close"].ewm(span=26, adjust=False).mean()
    c["macd"] = ema12 - ema26
    c["macd_signal"] = c["macd"].ewm(span=9, adjust=False).mean()

    prev_close = c["close"].shift(1)
    tr = pd.concat([
        c["high"] - c["low"],
        (c["high"] - prev_close).abs(),
        (c["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    c["atr"] = tr.ewm(span=14, adjust=False).mean()
    c["vma"] = c["volume"].rolling(20).mean()

    x = c.iloc[-1]
    prev = c.iloc[-2]
    price = float(x["close"])
    ema20 = float(x["ema20"])
    ema50 = float(x["ema50"])
    rsi = float(x["rsi"]) if pd.notna(x["rsi"]) else 50.0
    macd = float(x["macd"])
    macd_signal = float(x["macd_signal"])
    atr = float(x["atr"]) if pd.notna(x["atr"]) else 0.0
    volume_ratio = float(x["volume"] / x["vma"]) if pd.notna(x["vma"]) and x["vma"] > 0 else 1.0

    score = 0
    reasons = []
    bullish = bearish = 0

    if ema20 > ema50:
        score += 2; bullish += 1; reasons.append("روند EMA صعودی")
    elif ema20 < ema50:
        score -= 2; bearish += 1; reasons.append("روند EMA نزولی")

    if macd > macd_signal:
        score += 2; bullish += 1; reasons.append("MACD صعودی")
    elif macd < macd_signal:
        score -= 2; bearish += 1; reasons.append("MACD نزولی")

    if 52 <= rsi <= 68:
        score += 1; bullish += 1; reasons.append("RSI در ناحیه مومنتوم خرید")
    elif 32 <= rsi <= 48:
        score -= 1; bearish += 1; reasons.append("RSI در ناحیه مومنتوم فروش")
    elif rsi > 72:
        reasons.append("RSI بیش‌خرید؛ ورود خرید فیلتر شد")
    elif rsi < 28:
        reasons.append("RSI بیش‌فروش؛ ورود فروش فیلتر شد")

    if volume_ratio >= 1.10:
        score += 1 if score > 0 else -1
        reasons.append("حجم بالاتر از میانگین")

    # Avoid chasing a move that is already too extended relative to ATR.
    extension = abs(price - ema20) / atr if atr > 0 else 0
    if extension > 2.5:
        if score > 0:
            score -= 1
        elif score < 0:
            score += 1
        reasons.append("فاصله قیمت از EMA زیاد است")

    # Basic confirmation from the latest candle direction.
    if float(x["close"]) > float(x["open"]):
        bullish += 1
    elif float(x["close"]) < float(x["open"]):
        bearish += 1

    if score >= 3 and bullish >= 2:
        signal = "BUY"
    elif score <= -3 and bearish >= 2:
        signal = "SELL"
    else:
        signal = "HOLD"

    confidence = min(95, 50 + abs(score) * 8 + abs(bullish - bearish) * 4)
    if signal != "HOLD" and confidence < min_confidence:
        signal = "HOLD"
        reasons.append("اعتماد به حداقل تنظیم‌شده نرسید")
        confidence = min(confidence, max(0, min_confidence - 1))

    trend = "BULLISH" if ema20 > ema50 else "BEARISH" if ema20 < ema50 else "NEUTRAL"

    return {
        "signal": signal,
        "confidence": int(confidence),
        "price": round(price, 8),
        "rsi": round(rsi, 2),
        "ema20": round(ema20, 8),
        "ema50": round(ema50, 8),
        "macd": round(macd, 8),
        "macd_signal": round(macd_signal, 8),
        "atr": round(atr, 8),
        "volume_ratio": round(volume_ratio, 3),
        "trend": trend,
        "extension_atr": round(extension, 3),
        "reason": "، ".join(dict.fromkeys(reasons)) or "شرایط کافی برای ورود وجود ندارد.",
        "candles": len(c),
        "candle_time": str(c.index[-1])
    }
