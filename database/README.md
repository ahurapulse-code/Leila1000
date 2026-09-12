# Database

PostgreSQL منبع اصلی داده است و تغییرات فقط از مسیر Alembic انجام می‌شود.

## ترتیب migration فعلی

- `0001_initial`: workspace، کاربران، عضویت‌ها، مستأجران و احراز هویت
- `0002_finance_features`: هزینه‌ها و تعهدات
- `0003_canonical_transactions`: حذف جدول پرداخت موازی و انتقال آن به `transactions`؛ این همان مدل canonical نسخهٔ سالم است
- `0004_archive_settings`: بایگانی durable و تنظیمات workspace

از تغییر مستقیم جدول‌ها یا افزودن مسیر دوم برای پرداخت‌ها خودداری کنید. API پرداخت مستأجر به جدول `transactions` می‌نویسد؛ ودیعه و اجاره با `kind` از هم جدا می‌شوند.

برای پشتیبان‌گیری، از خروجی `/api/export` و همچنین dump واقعی PostgreSQL استفاده کنید. خروجی JSON جایگزین backup دیتابیس نیست.
