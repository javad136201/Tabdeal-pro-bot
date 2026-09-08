import sqlite3,json
from pathlib import Path
import pandas as pd
class Store:
    def __init__(self,path):
        self.path=path;Path(path).parent.mkdir(parents=True,exist_ok=True)
        with sqlite3.connect(path) as c:c.execute('CREATE TABLE IF NOT EXISTS candles(symbol TEXT,interval TEXT,ts INTEGER,open REAL,high REAL,low REAL,close REAL,volume REAL,PRIMARY KEY(symbol,interval,ts))')
    def save(self,symbol,interval,df):
        rows=[]
        for i,r in df.iterrows():rows.append((symbol,interval,int(pd.Timestamp(i).timestamp()),float(r.open),float(r.high),float(r.low),float(r.close),float(r.volume)))
        if rows:
            with sqlite3.connect(self.path) as c:c.executemany('INSERT OR REPLACE INTO candles VALUES(?,?,?,?,?,?,?,?)',rows)
    def log(self,engine,event,data):
        import json,sqlite3
        # no-op event sink in this lightweight build; trades remain in the engine state
    def load(self,symbol,limit=4000):
        with sqlite3.connect(self.path) as c:r=c.execute('SELECT ts,open,high,low,close,volume FROM candles WHERE symbol=? ORDER BY ts DESC LIMIT ?',(symbol,limit)).fetchall()
        r=list(reversed(r));
        if not r:return pd.DataFrame(columns=['open','high','low','close','volume'])
        return pd.DataFrame([x[1:] for x in r],index=pd.to_datetime([x[0] for x in r],unit='s',utc=True),columns=['open','high','low','close','volume'])
