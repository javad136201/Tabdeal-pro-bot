import pandas as pd, numpy as np
from app.strategy import analyze
from app.data import trades_to_1m
idx=pd.date_range('2026-01-01',periods=1200,freq='min',tz='UTC');p=100+np.arange(1200)*.02+np.sin(np.arange(1200)/18)*.1
c=pd.DataFrame({'open':p,'high':p+.1,'low':p-.1,'close':p,'volume':10.0},index=idx)
a=analyze(c);assert 'signal' in a and 'confidence' in a
raw=[{'price':'100','qty':'1','time':int(idx[0].timestamp()*1000)},{'price':'101','qty':'1','time':int((idx[0]+pd.Timedelta(seconds=20)).timestamp()*1000)}]
assert len(trades_to_1m(raw))==1
print('ALL TESTS PASS')
