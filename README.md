# Tabdeal Pro 5.0

نسخه ساده و پایدار برای Railway.

- Dashboard فارسی
- Demo خودکار با شروع برنامه
- دریافت معاملات عمومی Tabdeal
- ساخت کندل 1 دقیقه
- EMA20/EMA50 + RSI + MACD + Volume
- TP / SL / بستن دستی
- سود و زیان USD
- Backtest با CSV
- Live trading عمداً قفل است

نکته: داده تاریخی رسمی OHLCV در API عمومیِ بررسی‌شده برای این پروژه در دسترس/شفاف نبود؛ بنابراین Backtest فقط CSV واقعی کاربر را می‌پذیرد و داده جعلی تولید نمی‌کند.

Start:
uvicorn app.main:app --host 0.0.0.0 --port $PORT
