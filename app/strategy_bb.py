"""
استراتژی دوم و مستقل: میانگین‌گرا (Mean Reversion) بر پایه‌ی
Bollinger Bands + Stochastic Oscillator.

هدف این ماژول، تایید یا رد سیگنال استراتژی اصلی (روندی: EMA/RSI/MACD) است.
وقتی هر دو استراتژی هم‌جهت باشند، اعتماد بیشتر می‌شود؛ وقتی مخالف باشند،
برای احتیاط سیگنال نهایی خنثی (HOLD) می‌شود.
"""


def bollinger(closes, n=20, k=2.0):
    if len(closes) < n:
        return None
    window = closes[-n:]
    mean = sum(window) / n
    var = sum((x - mean) ** 2 for x in window) / n
    sd = var ** 0.5
    return {"mid": mean, "upper": mean + k * sd, "lower": mean - k * sd, "sd": sd}


def stochastic_k(candles, n=14):
    if len(candles) < n:
        return None
    window = candles[-n:]
    highs = [c["high"] for c in window]
    lows = [c["low"] for c in window]
    hh, ll = max(highs), min(lows)
    close = candles[-1]["close"]
    if hh == ll:
        return 50.0
    return (close - ll) / (hh - ll) * 100.0


def analyze_bb(candles):
    closes = [c["close"] for c in candles]
    bb = bollinger(closes, 20, 2.0)
    k = stochastic_k(candles, 14)
    if bb is None or k is None:
        return {"signal": "HOLD", "confidence": 0, "reason": "داده کافی نیست برای Bollinger/Stochastic"}

    price = closes[-1]
    score = 0
    reasons = []

    if price <= bb["lower"]:
        score += 30
        reasons.append("قیمت زیر باند پایین Bollinger (اشباع فروش)")
    elif price >= bb["upper"]:
        score -= 30
        reasons.append("قیمت بالای باند بالای Bollinger (اشباع خرید)")

    if k < 20:
        score += 20
        reasons.append("Stochastic در ناحیه اشباع فروش")
    elif k > 80:
        score -= 20
        reasons.append("Stochastic در ناحیه اشباع خرید")

    if score >= 30:
        sig = "BUY"
    elif score <= -30:
        sig = "SELL"
    else:
        sig = "HOLD"

    conf = min(99, max(1, 50 + abs(score))) if sig != "HOLD" else 0

    return {
        "signal": sig,
        "confidence": round(conf, 1),
        "reason": "، ".join(reasons) if reasons else "خنثی",
        "bb_upper": round(bb["upper"], 6),
        "bb_mid": round(bb["mid"], 6),
        "bb_lower": round(bb["lower"], 6),
        "stoch_k": round(k, 2),
    }
