# Tabdeal Pro v2.3

نسخه Demo حرفه‌ای با کنترل کاربر روی حد سود، حد ضرر و Trailing Stop.

- داشبورد فارسی و موبایل‌پسند
- TP/SL/Trailing قابل تنظیم از داخل داشبورد
- تغییر تنظیمات برای معامله فعلی و معاملات بعدی
- بستن دستی معامله
- Pause / Resume
- تاریخچه معاملات
- EMA20 / EMA50 / RSI14 / Volume
- Live trading عمداً قفل است

API جدید:
`POST /api/demo/risk`
با بدنه JSON:
`{"take_profit_pct":1.5,"stop_loss_pct":1.0,"trailing_stop_pct":0.5}`

کلید API واقعی را در GitHub قرار ندهید.
