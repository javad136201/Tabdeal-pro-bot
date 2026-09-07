# Tabdeal Pro v3.0

داشبورد فارسی یکپارچه برای Demo، Forward Test، Backtest و پنل Live.

## نکات مهم
- LIVE_TRADING_ENABLED به صورت پیش‌فرض false است.
- برای Live علاوه بر این متغیر، DASHBOARD_PASSWORD و API Key/Secret لازم است.
- کلید API هرگز در GitHub قرار نگیرد.
- Backtest حرفه‌ای از CSV با ستون‌های timestamp, open, high, low, close, volume پشتیبانی می‌کند.
- Forward Test از داده زنده بازار استفاده می‌کند ولی سفارش واقعی ارسال نمی‌کند.

## تبادل
این پروژه بر مبنای endpointهای رسمی فعلی Tabdeal برای trades، exchangeInfo، account و order ساخته شده است. قبل از Live حتماً preflight را اجرا کنید و API را بدون برداشت بسازید.
