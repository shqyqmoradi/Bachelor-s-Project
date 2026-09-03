# مقایسهٔ عملی SQL Server، PostgreSQL و MongoDB در فروشگاه آنلاین

این مخزن یک آزمایش دانشگاهی بازتولیدپذیر است که سناریوی منطقی یکسانی را در
SQL Server 2022، PostgreSQL 16 و MongoDB 7 پیاده‌سازی می‌کند. خروجی شامل Schema،
مدل سندی، ERD، داده‌ساز قطعی، ۱۶ عملیات، دو فاز Index، پایش منابع، Backup/Restore،
CSV/JSON، نمودار و گزارش است. هیچ نتیجهٔ ساختگی در مخزن وجود ندارد.

## طراحی آزمایش

- مقیاس `--orders` تعداد سفارش‌هاست؛ تعداد Customer برابر `max(1000, orders/5)`
  و Product برابر `max(1000, orders/10)` است. تعداد دقیق همهٔ موجودیت‌ها در
  `insert_results.csv` ثبت می‌شود. یک سفارش ۱ تا ۵ قلم دارد.
- Seed پیش‌فرض `20260830` است. همهٔ مقادیر با ID و Seed تولید می‌شوند؛ بنابراین
  سه Loader دقیقاً همان شناسه، تاریخ، وضعیت، قیمت و جمع مالی را می‌بینند.
- پول با `Decimal` و دقت دو رقم اعشار تولید می‌شود؛ زمان‌ها UTC هستند.
- اجرای Query کاملاً ترتیبی است. هر Query یک warm-up بدون زمان‌گیری و سپس ۱۰
  اجرای زمان‌دار دارد. `perf_counter()` زمان wall-clock را ثبت می‌کند.
- CPU و RAM کل Host هر ۱۰۰ ms نمونه‌برداری می‌شوند. این اندازه‌گیری شامل سربار
  سیستم و Docker است؛ بستن برنامه‌های دیگر و اجرای ترتیبی برای مقایسه الزامی است.
- فاز اول فقط Indexهای PK/UNIQUE اجباری را دارد؛ فاز دوم Indexهای workload را
  اضافه می‌کند. Indexهای اجباری حذف نمی‌شوند چون حذفشان معنای Schema را عوض می‌کند.
- Cold cache به‌دلیل نبود روش هم‌ارز بین سه موتور خودکار نشده است؛ پروتکل دقیق در
  [cold_cache_methodology.md](report/cold_cache_methodology.md) آمده است.

## پیش‌نیازها

- Docker Desktop با حداقل ۱۲ GB RAM قابل تخصیص، ۶ هسته و حدود ۳۰ GB فضای آزاد
- Python 3.11 یا 3.12
- GNU Make (اختیاری)
- Microsoft ODBC Driver 18 for SQL Server روی Host

روی macOS:

```bash
brew install unixodbc
brew install --cask microsoft-odbc-driver-for-sql-server
```

تصویر SQL Server فقط `linux/amd64` است. روی Apple Silicon با emulation اجرا می‌شود؛
این وضعیت برای نتیجهٔ نهایی منصفانه نیست، چون فقط SQL Server هزینهٔ emulation دارد.
برای Benchmark قابل دفاع، یک Host x86-64 Linux/Windows استفاده کنید. اگر هدف صرفاً
آزمایش صحت است، Docker Desktop روی Apple Silicon کافی است و محدودیت باید در گزارش ثبت شود.

## نسخه‌های ثابت آزمایش

| سیستم | Image |
|---|---|
| SQL Server | `mcr.microsoft.com/mssql/server:2022-CU16-ubuntu-22.04` (Developer) |
| PostgreSQL | `postgres:16.4-bookworm` |
| MongoDB | `mongo:7.0.14-jammy` (Community) |

Tagها ثابت‌اند ولی برای آرشیو بلندمدت بهتر است پس از اولین Pull، digest واقعی
`docker image inspect` نیز در گزارش ثبت شود. موتور Benchmark نسخهٔ runtime را در
`storage_results.csv` ذخیره می‌کند.

## نصب از صفر

```bash
cd Bachelor-s-Project
make env
```

فایل `.env` از `.env.example` ساخته می‌شود. Credentialهای نمونه فقط برای شبکهٔ
محلی آزمایش هستند؛ برای Production باید Secret manager، TLS و حساب‌های کم‌اختیار
استفاده شود.

Docker Desktop را اجرا کنید، سپس:

```bash
make up
docker compose ps
```

تا `healthy` شدن هر سه سرویس صبر کنید. Resource limit هر سرویس ۲ CPU و ۴ GB RAM
است. با این دستور اعمال واقعی محدودیت‌ها را کنترل کنید:

```bash
docker inspect online-shop-benchmark-postgres-1 --format '{{.HostConfig.NanoCpus}} {{.HostConfig.Memory}}'
```

## اجرای کامل Benchmark

فرمان زیر Schemaها را از نو می‌سازد، برای هر دیتابیس دادهٔ canonical بار می‌کند،
هر دو فاز Index را اجرا می‌کند و نتایج/نمودارها را تولید می‌کند:

```bash
ORDERS=100000 REPETITIONS=10 make benchmark
```

مقیاس‌های پشتیبانی‌شده:

```bash
.venv/bin/python -m benchmark.run_all --orders 10000
.venv/bin/python -m benchmark.run_all --orders 100000
.venv/bin/python -m benchmark.run_all --orders 500000
.venv/bin/python -m benchmark.run_all --orders 1000000
```

برای اجرای مستقل یا ادامه روی دادهٔ موجود:

```bash
.venv/bin/python -m benchmark.setup_databases --database postgresql
.venv/bin/python -m benchmark.load_data --database postgresql --orders 100000
.venv/bin/python -m benchmark.run_all --database postgresql --skip-load
```

`setup_databases` دادهٔ قبلی همان Schema را حذف می‌کند. این رفتار فقط برای محیط
آزمایشی است. Benchmarkهای سه موتور را هم‌زمان اجرا نکنید.

## Backup و Restore واقعی

پس از بارگذاری داده:

```bash
.venv/bin/python -m benchmark.backup_restore_benchmark
```

این برنامه برای هر موتور Backup می‌گیرد، آن را در دیتابیس جداگانهٔ
`OnlineShopDB_restore` بازمی‌گرداند، زمان و اندازهٔ فایل را در
`results/backup_restore_results.csv` می‌نویسد. دستورهای مستقل در پوشهٔ هر موتور
مستند شده‌اند. برای ارزیابی درست، Restore موفق را با شمارش رکورد و Queryهای Q01/Q06
نیز کنترل کنید و دیتابیس restore را جزو اندازهٔ دیتابیس اصلی حساب نکنید.

## خروجی‌ها

- `results/raw_results.csv`: هر اجرای خام Query با زمان و منابع
- `results/summary_results.csv`: Average/Min/Max/Median/StdDev
- `results/insert_results.csv`: زمان بارگذاری Dataset canonical
- `results/storage_results.csv`: data/index/total size و نسخهٔ موتور
- `results/results.json`: همهٔ نتایج و metadata
- `results/environment.json`: OS، Python، CPU، RAM و تنظیمات
- `results/backup_restore_results.csv`: زمان/حجم Backup و Restore
- `results/final_comparison.csv`: جدول نهایی عددی پس از اجرای `benchmark.analyze_results`
- `charts/*.png`: نمودارهای ساخته‌شده فقط از نتایج واقعی

اعتبارسنجی:

```bash
make validate
```

`validate_results` وجود و غیرخالی بودن فایل‌ها و پرچم `is_real=true` را کنترل می‌کند.
پس از آن `make analyze` جدول نهایی و بخش نتایج اندازه‌گیری‌شده را تولید می‌کند.
برای کنترل استاتیک پیش از وجود نتایج از `make check` استفاده کنید.

## ساختار فایل‌ها

```text
sqlserver/     schema, indexes, queries, security, backup/restore
postgresql/    schema, indexes, queries, security, backup/restore
mongodb/       validators/document model, indexes, queries, roles, backup/restore
benchmark/     generator, loaders, runners, monitor, charts, validation
report/        ERD, methodology, rubric and final academic report
results/       generated real measurements (initially empty)
charts/        generated figures (initially empty)
backups/       generated backup media (git-ignored)
```

## منصفانه نگه‌داشتن اجرا

قبل از هر Run، نسخه و digest Imageها، مدل CPU، RAM، OS، Docker version، نوع Disk،
Power mode و برنامه‌های فعال را ثبت کنید. سرویس‌های غیرضروری را ببندید، Host را به
برق وصل کنید، thermal throttling را کنترل کنید، ترتیب سه دیتابیس را در چند دور
تصادفی کنید و Median چند دور را گزارش دهید. یک بار اجرای ترتیبی اثر order را حذف
نمی‌کند. Logging/Auditing/TLS باید یا برای هر سه خاموشِ آزمایشگاهی یا برای هر سه با
سیاست معادل فعال باشد و تصمیم ثبت شود.

## پاک‌سازی

```bash
make down
docker compose down -v   # مخرب: همهٔ volumeهای آزمایشی این Compose حذف می‌شوند
make clean-results       # فقط CSV/JSON/PNG تولیدشده را حذف می‌کند
```

## نکات تفسیری

Q01، Q02، Q03، Q04، Q06، Q07، Q10، Q11 و mutationها مقایسهٔ مستقیم‌تری دارند.
Q05 در MongoDB به دلیل embedding، تعداد round/lookup متفاوتی دارد. Q08/Q09/Q12/Q13
از نظر خروجی منطقی معادل‌اند ولی هزینهٔ JOIN رابطه‌ای و `$lookup/$unwind` سندی
هم‌ساخت نیست؛ این تفاوت خود بخشی از معماری مورد مطالعه است، نه خطای Benchmark.
نتیجه‌گیری نهایی باید فقط پس از تولید CSV واقعی نوشته شود.
