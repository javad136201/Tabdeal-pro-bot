def signal(df):
    if len(df)<20:return {'signal':'HOLD','score':0}
    ema20=df.close.ewm(span=20).mean().iloc[-1]; ema50=df.close.ewm(span=50).mean().iloc[-1]
    score=1 if ema20>ema50 else -1
    return {'signal':'BUY' if score>0 else 'SELL','score':score,'price':float(df.close.iloc[-1])}
