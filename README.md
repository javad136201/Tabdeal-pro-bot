# Tabdeal Pro Final v2.1 — Persian Trading Dashboard

User-friendly Persian dashboard for DEMO and controlled LIVE preparation.

### Dashboard features
- Clear BUY / SELL / HOLD signal
- Current price, confidence, RSI, EMA20/EMA50
- Position status: open/flat
- Entry price, equity, quote/base balances
- Take-profit and stop-loss percentages and calculated prices
- Manual close for DEMO
- Demo reset and manual tick
- Last trades table with reason (signal / take-profit / stop-loss / manual)
- Backtest summary
- Emergency-stop and risk controls retained

### Safety
- LIVE remains disabled unless explicitly configured in Railway Variables.
- Never put API keys in GitHub.
- Test DEMO first, then LIVE preflight, then a very small real order.
- This release does not promise profitability.

### Endpoints
- `/`
- `/api/status`
- `/api/analysis`
- `/api/demo/state`
- `POST /api/demo/settings`
- `POST /api/demo/tick`
- `POST /api/demo/close`
- `POST /api/demo/reset`
- `/api/backtest`
- `/api/live/preflight`
- `POST /api/live/buy`
- `POST /api/live/close`
- `POST /api/live/stop`
- `POST /api/live/resume`
