
def analyze(candles, min_confidence=60):
    if candles is None or len(candles) < 55:
        return {
            "signal":"HOLD","confidence":0,"price":None,"rsi":None,
            "ema20":None,"ema50":None,"volume_ratio":None,
            "candles":0 if candles is None else len(candles),
            "reason":"برای تحلیل حداقل ۵۵ کندل لازم است."
        }
    c = candles.copy()
    c["ema20"] = c.close.ewm(span=20, adjust=False).mean()
    c["ema50"] = c.close.ewm(span=50, adjust=False).mean()
    d = c.close.diff()
    g = d.clip(lower=0).rolling(14).mean()
    l = (-d.clip(upper=0)).rolling(14).mean()
    rs = g / l.replace(0, None)
    c["rsi"] = 100 - 100/(1+rs)
    c["vma"] = c.volume.rolling(20).mean()

    x = c.iloc[-1]
    p = float(x.close)
    e20 = float(x.ema20)
    e50 = float(x.ema50)
    rsi = float(x.rsi) if x.rsi == x.rsi else 50.0
    vr = float(x.volume/x.vma) if x.vma and x.vma == x.vma else 1.0

    score = 0
    reasons = []

    if e20 > e50:
        score += 1
        reasons.append("روند کوتاه‌مدت صعودی")
    elif e20 < e50:
        score -= 1
        reasons.append("روند کوتاه‌مدت نزولی")

    if 52 <= rsi <= 70:
        score += 1
        reasons.append("RSI از مومنتوم خرید حمایت می‌کند")
    elif 30 <= rsi <= 48:
        score -= 1
        reasons.append("RSI از مومنتوم فروش حمایت می‌کند")

    if vr >= 1.05:
        score += 1 if score >= 0 else -1
        reasons.append("حجم تأییدکننده است")

    raw_conf = 50 + abs(score) * 15
    if score >= 2:
        signal = "BUY"
    elif score <= -2:
        signal = "SELL"
    else:
        signal = "HOLD"

    confidence = min(95, raw_conf)
    if signal != "HOLD" and confidence < min_confidence:
        signal = "HOLD"
        reasons.append("اعتماد به حداقل تنظیم‌شده نرسیده است.")
        confidence = min(confidence, min_confidence - 1)

    return {
        "signal": signal,
        "confidence": confidence,
        "price": round(p, 8),
        "rsi": round(rsi, 2),
        "ema20": round(e20, 8),
        "ema50": round(e50, 8),
        "volume_ratio": round(vr, 3),
        "candles": len(c),
        "reason": "، ".join(reasons) or "شرایط قوی دیده نشد."
    }
