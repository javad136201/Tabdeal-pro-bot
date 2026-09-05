# Tabdeal Pro Trading Bot

Professional starter architecture for Railway + GitHub + Tabdeal.

Modes:
- BACKTEST: historical/local OHLCV simulation
- DEMO: live market data, simulated orders
- LIVE: real Tabdeal orders (disabled by default)

Dashboard is served by FastAPI and is mobile friendly.

## Security
Never commit API keys. Put them only in Railway Variables.
Create a Tabdeal API key with trading permission only; do not enable withdrawals.

## Run locally
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload

## Railway
Deploy this repository as a Python service.
Start command:
uvicorn app.main:app --host 0.0.0.0 --port $PORT

Required first variables:
APP_ENV=railway
TRADING_MODE=DEMO
SECRET_KEY=generate-a-long-random-secret
TRADE_AMOUNT_IRT=1000000
TABDEAL_API_KEY=
TABDEAL_API_SECRET=

Keep TRADING_MODE=DEMO until the complete workflow has been tested.
