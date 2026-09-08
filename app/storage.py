
import sqlite3
from pathlib import Path
import pandas as pd
from .config import settings

class MarketStore:
    def __init__(self, path=None):
        self.path=path or settings.db_path
        Path(self.path).parent.mkdir(parents=True,exist_ok=True)
        self._init()

    def _conn(self):
        c=sqlite3.connect(self.path,check_same_thread=False)
        c.execute("PRAGMA journal_mode=WAL")
        return c

    def _init(self):
        with self._conn() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS candles(
                symbol TEXT NOT NULL,
                interval TEXT NOT NULL,
                ts INTEGER NOT NULL,
                open REAL, high REAL, low REAL, close REAL, volume REAL,
                PRIMARY KEY(symbol,interval,ts)
            )""")
            c.commit()

    def upsert(self,symbol,interval,df):
        if df is None or df.empty:return
        rows=[]
        for idx,r in df.iterrows():
            ts=int(pd.Timestamp(idx).timestamp())
            rows.append((symbol,interval,ts,float(r.open),float(r.high),float(r.low),float(r.close),float(r.volume)))
        with self._conn() as c:
            c.executemany("""INSERT OR REPLACE INTO candles
                (symbol,interval,ts,open,high,low,close,volume) VALUES(?,?,?,?,?,?,?,?)""",rows)
            c.commit()

    def load(self,symbol,interval="1m",limit=5000):
        with self._conn() as c:
            rows=c.execute("""SELECT ts,open,high,low,close,volume FROM candles
                              WHERE symbol=? AND interval=? ORDER BY ts DESC LIMIT ?""",
                           (symbol,interval,limit)).fetchall()
        if not rows:return pd.DataFrame(columns=["open","high","low","close","volume"])
        rows=list(reversed(rows))
        idx=pd.to_datetime([r[0] for r in rows],unit="s",utc=True)
        return pd.DataFrame([r[1:] for r in rows],index=idx,columns=["open","high","low","close","volume"])

    def count(self,symbol,interval="1m"):
        with self._conn() as c:
            return c.execute("SELECT COUNT(*) FROM candles WHERE symbol=? AND interval=?",(symbol,interval)).fetchone()[0]
