import math
from .strategy_bb import analyze_bb


def ema_series(values, n):
    """برمی‌گرداند لیست EMA برای هر نقطه (به‌جای بازسازی کامل هر بار)."""
    if not values:
        return []
    a = 2 / (n + 1)
    out = [values[0]]
    e = values[0]
    for v in values[1:]:
        e = a * v + (1 - a) * e
        out.append(e)
    return out


def ema(values, n):
    s = ema_series(values, n)
    return s[-1] if s else None


def rsi(values, n=14):
    if len(values) < n + 1:
        return None
    gains = []
    losses = []
    for a, b in zip(values[-n - 1:-1], values[-n:]):
        d = b - a
        gains.append(max(d, 0))
        losses.append(max(-d, 0))
    ag = sum(gains) / n
    al = sum(losses) / n
    if al == 0:
        return 100.0
    return 100 - 100 / (1 + ag / al)


def atr(c, n=14):
    if len(c) < n + 1:
        return None
    tr = []
    for i in range(1, len(c)):
        h, l, pc = c[i]["high"], c[i]["low"], c[i - 1]["close"]
        tr.append(max(h - l, abs(h - pc), abs(l - pc)))
    return sum(tr[-n:]) / n


def analyze(c):
    if len(c) < 55:
        return {"signal": "HOLD", "confidence": 0, "reason": "داده کافی نیست", "ready": False}

    closes = [x["close"] for x in c]
    vols = [x["volume"] for x in c]
    e20 = ema(closes, 20)
    e50 = ema(closes, 50)
    rr = rsi(closes, 14)
    aa = atr(c, 14)

    # محاسبه‌ی EMA و MACD به صورت O(n) با یک پاس روی داده (قبلاً هر نقطه
    # از صفر با ema(closes[:i]) دوباره حساب می‌شد که O(n^2) بود).
    fast_series = ema_series(closes, 12)
    slow_series = ema_series(closes, 26)
    macd_series = [f - s for f, s in zip(fast_series, slow_series)]
    signal_series = ema_series(macd_series, 9) if macd_series else []
    macd = macd_series[-1] if macd_series else None
    signal_line = signal_series[-1] if signal_series else None

    avgvol = sum(vols[-20:]) / 20 if len(vols) >= 20 else 0
    vol_ok = vols[-1] >= avgvol * 1.05 if avgvol else False

    score = 0
    reasons = []
    if e20 > e50:
        score += 25
        reasons.append("روند صعودی EMA")
    else:
        score -= 25
        reasons.append("روند نزولی EMA")
    if rr is not None:
        if rr > 52 and rr < 72:
            score += 20
            reasons.append("RSI صعودی")
        elif rr < 45:
            score -= 20
            reasons.append("RSI ضعیف")
    if macd is not None and signal_line is not None:
        if macd > signal_line:
            score += 25
            reasons.append("MACD مثبت")
        else:
            score -= 25
            reasons.append("MACD منفی")
    if vol_ok:
        score += 15 if score > 0 else -15
        reasons.append("حجم تأیید می‌کند")

    if score >= 55:
        primary_sig = "BUY"
    elif score <= -55:
        primary_sig = "SELL"
    else:
        primary_sig = "HOLD"
    primary_conf = min(99, max(1, 50 + abs(score) / 2))

    # --- استراتژی دوم و مستقل: Bollinger Bands + Stochastic (میانگین‌گرا) ---
    bb = analyze_bb(c)

    final_sig = primary_sig
    final_conf = primary_conf
    confirmed = False
    if primary_sig != "HOLD":
        if bb["signal"] == primary_sig:
            confirmed = True
            final_conf = min(99, primary_conf + 10)
        elif bb["signal"] != "HOLD":
            # دو استراتژی مخالف هم هستند؛ برای احتیاط معامله را خنثی می‌کنیم
            final_sig = "HOLD"
            final_conf = max(1, primary_conf - 20)

    reason_txt = "، ".join(reasons)
    if bb["signal"] != "HOLD":
        tag = "تایید شد ✅" if confirmed else "رد شد ⚠️"
        reason_txt += f" | استراتژی دوم (Bollinger/Stochastic): {bb['reason']} → {tag}"

    return {
        "ready": True,
        "signal": final_sig,
        "confidence": round(final_conf, 1),
        "primary_signal": primary_sig,
        "primary_confidence": round(primary_conf, 1),
        "confirmed": confirmed,
        "price": closes[-1],
        "rsi": round(rr, 2) if rr is not None else None,
        "ema20": e20,
        "ema50": e50,
        "macd": macd,
        "macd_signal": signal_line,
        "atr": aa,
        "volume": vols[-1],
        "volume_avg": avgvol,
        "bb_signal": bb["signal"],
        "bb_confidence": bb["confidence"],
        "bb_reason": bb["reason"],
        "reason": reason_txt,
    }
