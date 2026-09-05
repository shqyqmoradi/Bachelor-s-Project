# Practical Comparison of SQL Server, PostgreSQL and MongoDB

این پروژه مربوط به پروژه دانشگاهی مقطع کارشناسی مهندسی کامپیوتر ـ نرم‌افزار در دانشگاه شیراز است.

در این پروژه سه سیستم مدیریت پایگاه داده `SQL Server`، `PostgreSQL` و `MongoDB` در یک سناریوی یکسان فروشگاه آنلاین با هم مقایسه شده‌اند.

هدف اصلی پروژه بررسی تفاوت این سه سیستم از نظر ساختار داده، Query Performance، تأثیر Index، زمان Insert/Update/Delete، مصرف منابع، حجم ذخیره‌سازی و Backup/Restore است.

## ساختار فروشگاه آنلاین

مدل پروژه شامل ۸ موجودیت اصلی است:

- Customers
- Categories
- Products
- Orders
- OrderItems
- Payments
- Addresses
- Shipment

در `SQL Server` و `PostgreSQL` از مدل رابطه‌ای استفاده شده است.

در `MongoDB` داده‌ها با مدل سندی و استفاده از Embedded Documents و References طراحی شده‌اند.

## طراحی Benchmark

نتایج اصلی پروژه با ۱۰۰٬۰۰۰ سفارش ثبت شده‌اند.

برای تولید داده‌های یکسان در هر سه سیستم از Seed ثابت زیر استفاده شده است:

```text
20260830
```

هر سفارش بین ۱ تا ۵ آیتم دارد.

در مجموع ۱۶ عملیات برای Benchmark در نظر گرفته شده است:

- ۱۳ عملیات خواندن و تجمیع
- Insert
- Update
- Delete

هر عملیات خواندنی ۱۰ بار اجرا می‌شود و قبل از آن یک Warm-up انجام می‌شود.

Benchmark در دو مرحله اجرا می‌شود:

1. فقط Indexهای اصلی و اجباری
2. همراه با Indexهای مخصوص Workload

## نسخه‌های استفاده‌شده

| Database | Version |
|---|---|
| SQL Server | SQL Server 2022 |
| PostgreSQL | PostgreSQL 16.4 |
| MongoDB | MongoDB 7.0.14 |

اجرای پایگاه داده‌ها با Docker انجام می‌شود.

## پیش‌نیازها

- Docker Desktop
- Python 3.11 یا 3.12
- Microsoft ODBC Driver 18 for SQL Server
- GNU Make

نصب Driver روی macOS:

```bash
brew install unixodbc
brew install --cask microsoft-odbc-driver-for-sql-server
```

## اجرای پروژه

ابتدا فایل محیطی را بسازید:

```bash
make env
```

سپس سرویس‌ها را اجرا کنید:

```bash
make up
```

وضعیت Containerها:

```bash
docker compose ps
```

برای اجرای Benchmark اصلی:

```bash
ORDERS=100000 REPETITIONS=10 make benchmark
```

برای اجرای مستقیم با Python:

```bash
.venv/bin/python -m benchmark.run_all --orders 100000
```

## Backup و Restore

برای اجرای تست Backup و Restore:

```bash
.venv/bin/python -m benchmark.backup_restore_benchmark
```

نتایج در پوشه زیر ذخیره می‌شوند:

```text
results/
```

## خروجی‌های اصلی

مهم‌ترین فایل‌های نتیجه:

```text
results/raw_results.csv
results/summary_results.csv
results/insert_results.csv
results/storage_results.csv
results/environment.json
results/backup_restore_results.csv
results/restore_validation.csv
results/final_comparison.csv
```

برای بررسی صحت نتایج:

```bash
make validate
```

برای تحلیل نهایی:

```bash
make analyze
```

## ساختار پروژه

```text
benchmark/       benchmark scripts and data generator
mongodb/         MongoDB schema, queries and indexes
postgresql/      PostgreSQL schema, queries and indexes
results/         benchmark results
sqlserver/       SQL Server schema, queries and indexes
.env.example     environment configuration example
.gitignore
docker-compose.yml
Makefile
README.md
requirements.txt
```

## نکته درباره محیط اجرا

روی Macهای دارای Apple Silicon، SQL Server با Emulation اجرا می‌شود، چون Image رسمی آن بر پایه معماری `amd64` است.

به همین دلیل نتایج Performance روی Apple Silicon ممکن است کاملاً منصفانه نباشند و برای Benchmark دقیق‌تر بهتر است از یک سیستم `x86-64` استفاده شود.

## پاک‌سازی

برای متوقف کردن سرویس‌ها:

```bash
make down
```

برای حذف Volumeهای آزمایشی:

```bash
docker compose down -v
```

این پروژه با هدف مقایسه عملی سه پایگاه داده در یک محیط یکسان و بررسی تفاوت مدل رابطه‌ای و سندی انجام شده است.