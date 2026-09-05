# نتایج Benchmark

این پوشه شامل اندازه‌گیری‌های اجرای ۱۰۰٬۰۰۰ سفارش است. فایل `raw_results.csv`
۹۶۰ ردیف دارد:

```text
3 پایگاه داده × 2 فاز Index × 16 عملیات × 10 تکرار
```

فایل‌های `summary_results.csv`، `insert_results.csv`، `storage_results.csv`،
`backup_restore_results.csv` و `restore_validation.csv` نتایج خلاصه و عملیاتی را
نگه می‌دارند. فایل `measured-results.md` نسخهٔ خوانای جدول‌های خلاصه است.

برای بازتولید داده‌ها از `python -m benchmark.run_all`، برای Backup/Restore از
`python -m benchmark.backup_restore_benchmark` و برای ساخت جدول مقایسه و فایل
خوانای نتایج از `python -m benchmark.analyze_results` استفاده کنید.
