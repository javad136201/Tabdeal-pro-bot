# Tabdeal Pro Bot v1.3 — Demo Trading

This version adds:
- Live Tabdeal public market data
- EMA20 / EMA50 / RSI14 / volume confirmation
- DEMO virtual account
- BUY/SELL simulation with fees
- Duplicate-position protection
- Demo reset
- Simple trade-derived backtest endpoint
- Mobile dashboard

## Important
This version does NOT send real orders to Tabdeal. `live_enabled` is hard-coded false.
API secrets should be stored only in Railway Variables, not GitHub.

## Endpoints
- `/`
- `/health`
- `/api/status`
- `/api/market`
- `/api/analysis`
- `/api/demo/state`
- `POST /api/demo/tick`
- `POST /api/demo/reset`
- `/api/backtest`

The backtest currently uses 1-minute candles reconstructed from the currently available public trades. For a serious historical backtest, use a verified historical OHLCV dataset.
