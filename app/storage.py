import sqlite3
from pathlib import Path
from threading import RLock
import pandas as pd

class Store:
    def __init__(self,path):
        self.path=path
        self.lock=RLock()
        Path(path).parent.mkdir(parents=True,exist_ok=True)
        with self.lock, sqlite3.connect(path,timeout=15) as c:
            c.execute("PRAGMA journal_mode=WAL")
            c.execute("PRAGMA busy_timeout=15000")
            c.execute("CREATE TABLE IF NOT EXISTS candles(symbol TEXT,interval TEXT,ts INTEGER,open REAL,high REAL,low REAL,close REAL,volume REAL,PRIMARY KEY(symbol,interval,ts))")

    def save(self,symbol,interval,df):
        if df is None or df.empty:return 0
        rows=[]
        for i,r in df.iterrows():
            try: rows.append((symbol,interval,int(pd.Timestamp(i).timestamp()),float(r.open),float(r.high),float(r.low),float(r.close),float(r.volume)))
            except Exception: pass
        if not rows:return 0
        with self.lock, sqlite3.connect(self.path,timeout=15) as c:
            c.execute("PRAGMA busy_timeout=15000")
            c.executemany('INSERT OR REPLACE INTO candles VALUES(?,?,?,?,?,?,?,?)',rows)
            c.commit()
        return len(rows)

    def log(self,engine,event,data):
        return None

    def load(self,symbol,limit=4000):
        with self.lock, sqlite3.connect(self.path,timeout=15) as c:
            c.execute("PRAGMA busy_timeout=15000")
            r=c.execute('SELECT ts,open,high,low,close,volume FROM candles WHERE symbol=? ORDER BY ts DESC LIMIT ?', (symbol,int(limit))).fetchall()
        r=list(reversed(r))
        if not r:return pd.DataFrame(columns=['open','high','low','close','volume'])
        return pd.DataFrame([x[1:] for x in r],index=pd.to_datetime([x[0] for x in r],unit='s',utc=True),columns=['open','high','low','close','volume'])
