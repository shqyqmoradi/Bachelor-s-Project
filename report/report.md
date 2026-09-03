# تحلیل و مقایسهٔ SQL Server، PostgreSQL و MongoDB در سناریوی فروشگاه آنلاین

## چکیده

این پژوهش چارچوبی عملی و بازتولیدپذیر برای مقایسهٔ سه سامانهٔ مدیریت پایگاه داده
در یک بارکاری فروشگاه آنلاین ارائه می‌کند. هشت موجودیت منطقی مشترک، دادهٔ قطعی،
عملیات خواندن/تجمیع/نوشتن، دو وضعیت Index، پایش CPU/RAM، اندازهٔ ذخیره‌سازی و
Backup/Restore پوشش داده شده‌اند. تفاوت مدل سندی و رابطه‌ای عمداً حفظ شده است تا
هر موتور با مدل طبیعی خود آزمایش شود، در حالی که شناسه‌ها و واقعیت‌های تجاری یکسان
می‌مانند. Benchmark واقعی با ۱۰۰٬۰۰۰ سفارش و ۱۰ تکرار اجرا شد و بخش عددی با
`benchmark.run_all` و `benchmark.analyze_results` از داده‌های واقعی تولید شده است.

## 1. مقدمه

انتخاب پایگاه داده فقط مسابقهٔ سرعت نیست. قیود یکپارچگی، شکل Query، هزینهٔ توسعه،
مصرف منابع، عملیات بازیابی و کنترل‌های امنیتی بر تناسب یک محصول اثر دارند. فروشگاه
آنلاین نمونه‌ای مناسب است، زیرا هم تراکنش نقطه‌ای و هم گزارش تجمیعی، ارتباط چند
موجودیت و تاریخچهٔ مالی را در بر می‌گیرد.

## 2. بیان مسئله

مقایسه‌های عمومی معمولاً Schema و دادهٔ متفاوت، Cache کنترل‌نشده، Hardware متفاوت
یا مدل MongoDB شبیه جدول دارند. مسئلهٔ این پژوهش ساخت آزمایشی است که خروجی منطقی
مشترک داشته باشد، قابلیت‌های طبیعی هر معماری را از بین نبرد و محدودیت هم‌ارزی را
صریح گزارش کند.

## 3. اهداف

- طراحی کامل فروشگاه با Customer، Address، Category، Product، Order، OrderItem،
  Payment و Shipment؛
- ساخت مدل رابطه‌ای برای SQL Server/PostgreSQL و مدل سندی معنادار برای MongoDB؛
- سنجش Insert، Query، CPU، RAM، Storage، Backup و Restore؛
- مقایسهٔ مستند امنیت و effort؛
- تولید پروژه‌ای قابل تکرار بدون نتیجهٔ فرضی.

## 4. مروری بر SQL Server

SQL Server 2022 یک DBMS رابطه‌ای تجاری با T-SQL، optimizer هزینه‌محور، قیود
رابطه‌ای، تراکنش‌های ACID، ابزارهای مدیریتی و امکانات امنیتی گسترده است. آزمایش از
Developer edition استفاده می‌کند که برای توسعه ویژگی‌های Enterprise را دارد، اما
مجوز Production ندارد. تفاوت Editionها باید هنگام تعمیم نتیجه لحاظ شود؛ جدول رسمی
[SQL Server 2022 editions](https://learn.microsoft.com/en-us/sql/sql-server/editions-and-components-of-sql-server-2022) مرجع است.

## 5. مروری بر PostgreSQL

PostgreSQL یک DBMS رابطه‌ای متن‌باز با SQL غنی، MVCC، optimizer هزینه‌محور، انواع
داده و Extensionهاست. نسخهٔ 16.4 در محیط آزمایش Pin شده است. Role و privilege،
RLS، TLS و logging در هسته وجود دارند، در حالی که بعضی قابلیت‌ها مانند audit
ساخت‌یافته معمولاً با Extension یا ابزار بیرونی تکمیل می‌شوند.

## 6. مروری بر MongoDB

MongoDB یک پایگاه سندی BSON است. Aggregate pipeline، secondary index، validation
و replica/sharding محور اصلی آن‌اند. این پروژه Community 7.0.14 را به‌صورت تک‌گره
اجرا می‌کند؛ پس تراکنش چندسندی replica-set، High Availability و sharding موضوع
این آزمایش نیستند. امکانات Enterprise/Atlas نباید به Community نسبت داده شوند.

## 7. طراحی پایگاه فروشگاه

Customer ایمیل یکتا و وضعیت فعالیت دارد. هر Customer یک آدرس پیش‌فرض در Dataset
کنترل‌شده دارد. Product به Category تعلق دارد و قیمت/موجودی نامنفی است. Order
snapshot مالی Subtotal، Shipping، Discount و Total را نگه می‌دارد. UnitPrice داخل
OrderItem تاریخچهٔ قیمت را حفظ می‌کند. Payment و Shipment حتی پیش از تکمیل با
وضعیت `pending` ایجاد می‌شوند تا Cardinality در Dataset دقیقاً 1:1 باشد.

## 8. Schema رابطه‌ای و ERD

ERD کامل در [erd.md](erd.md) قرار دارد. روابط اصلی 1:N عبارت‌اند از
Customer–Address، Customer–Order، Category–Product، Order–OrderItem و
Product–OrderItem. روابط Order–Payment و Order–Shipment در این آزمایش 1:1 هستند.
PK، FK، UNIQUE، NOT NULL و CHECKها در هر دو Schema اعمال شده‌اند. SQL Server از
computed persisted columns و PostgreSQL از generated stored columns برای Total
استفاده می‌کند.

## 9. طراحی سندی MongoDB

چهار Collection وجود دارد: `customers`، `categories`، `products` و `orders`.
Address داخل Customer و Items/Payment/Shipment/shipping snapshot داخل Order قرار
می‌گیرند. Product و Category Reference هستند. دلیل embedding مالکیت، bounded بودن
و الگوی خواندن مشترک است؛ دلیل Reference اشتراک گسترده و lifecycle مستقل Catalog
است. Validation نوع Decimal/Date/ID و enumها را کنترل می‌کند، ولی Referential
Integrity در Loader است، زیرا MongoDB FK ندارد.

## 10. محیط تست

Compose برای هر سرویس سقف ۲ CPU و ۴ GiB تعریف می‌کند. Portها 1433، 5432 و 27017
هستند و Volume جدا دارند. پیش از نتیجه‌گیری باید خروجی runtime شامل OS، CPU، RAM،
Docker، digest Image و نسخهٔ موتور ثبت شود. SQL Server روی ARM emulated است؛ اجرای
نهایی منصفانه باید روی x86-64 باشد. سرویس‌ها در Benchmark هم‌زمان Query نمی‌گیرند.

## 11. تولید Dataset

Generator از Seed ثابت `20260830` و ID هر رکورد استفاده می‌کند. تاریخ‌ها در بازهٔ
چهارسالهٔ ثابت، قیمت‌ها Decimal، Statusها با توزیع مشخص و سفارش‌ها با ۱ تا ۵ قلم
ساخته می‌شوند. ایمیل، تلفن، شهر، SKU و tracking realistic ولی مصنوعی‌اند و دامنهٔ
`example.test` از تصادف با افراد واقعی جلوگیری می‌کند. مقیاس 10k تا 1m سفارش با
Batch پیش‌فرض 2000 پشتیبانی می‌شود.

## 12. روش Benchmark

برای هر دیتابیس چرخهٔ Setup، Insert canonical، حذف Indexهای اختیاری، Query phase،
ساخت Indexها، Query phase و Storage measurement انجام می‌شود. هر Query یک warm-up
و ۱۰ تکرار دارد. Average، Minimum، Maximum، Median و sample standard deviation از
wall-clock ms گزارش می‌شوند. ترتیب موتور در چند اجرای مستقل باید تصادفی شود تا اثر
گرما/ترتیب کاهش یابد.

## 13. آزمون Query

Q01 تا Q04 lookup و list، Q05 جزئیات کامل Order، Q06/Q07 فروش کل، Q08 محصول برتر،
Q09 فروش Category، Q10 میانگین سفارش، Q11 شمارش Status، Q12 Customer برتر و Q13
«Heavy Multi-Join / equivalent MongoDB Aggregation» است. سه عملیات نوشتن نیز
Insert/Update/Delete هستند؛ بنابراین در مجموع ۱۶ عملیات مستقل اجرا شده است. در SQL
mutationها Rollback و در MongoDB cleanup قطعی دارند. خروجی کامل در فایل‌های
`queries.sql/js` و کاتالوگ اجرایی Python موجود است.

## 14. آزمون Insert

`--orders 100000` به معنی 100,000 Order همراه Dimensionها، Itemها، Paymentها و
Shipmentهاست، نه 100,000 ردیف کل. این تعریف از قبل ثابت شده و تعداد واقعی هر نوع
رکورد در CSV درج می‌شود. Loader از batch یکسان استفاده می‌کند؛ با این حال embedding
باعث می‌شود تعداد عملیات physical write در MongoDB با تعداد ردیف‌های SQL برابر
نباشد. هر دو عدد logical و elapsed باید کنار هم گزارش شوند.

## 15. CPU و RAM

`psutil` کل Host را هر 100 ms نمونه‌برداری می‌کند و Average CPU، Average RAM و Peak
RAM را ثبت می‌کند. مزیت آن روش یکسان و محدودیت آن ورود بار Docker/OS و برنامه‌های
دیگر است. برای تحلیل دقیق‌تر می‌توان `docker stats --no-stream` و ابزارهای داخلی
موتور را به‌عنوان اندازه‌گیری ثانویه افزود، اما نباید با سری اصلی مخلوط کرد.

## 16. فضای ذخیره‌سازی

SQL Server از `sys.dm_db_partition_stats` و `sys.database_files`، PostgreSQL از
`pg_relation_size`/`pg_indexes_size`/`pg_database_size` و MongoDB از `dbStats`
استفاده می‌کند. `data_bytes` و `index_bytes` نزدیک‌ترین معیارهای منطقی‌اند؛
`total_bytes` شامل allocation داخلی متفاوت است و کاملاً هم‌معنا نیست. فشرده‌سازی،
WAL/log و preallocation باید در تفسیر ذکر شوند.

## 17. Backup و Restore

SQL Server `BACKUP DATABASE ... CHECKSUM`، PostgreSQL `pg_dump -Fc` و MongoDB
`mongodump --archive --gzip` دارند. Restore به نام جدا انجام می‌شود و با
`perf_counter` زمان‌گیری می‌گردد. SQL backup فیزیکی و دو مورد دیگر در این تنظیم
logical/archive هستند؛ بنابراین سرعتشان یک مقایسهٔ عملی workflow است، نه مقایسهٔ
الگوریتم کاملاً یکسان. صحت Restore باید با شمارش و Q01/Q06 بررسی شود.

## 18. مقایسهٔ امنیت

| قابلیت | SQL Server 2022 | PostgreSQL 16 | MongoDB 7 Community / Enterprise |
|---|---|---|---|
| Authentication | SQL/Windows/Kerberos | SCRAM، cert، GSSAPI، LDAP، PAM و... | Community: SCRAM/X.509؛ Enterprise/Atlas: LDAP/Kerberos نیز |
| Authorization/RBAC | Login/User/Role و GRANT/DENY | Role membership و object privileges | Role/user و built-in/custom roles |
| TLS | پشتیبانی TLS؛ Force Encryption قابل تنظیم | TLS بومی، الزام در `pg_hba.conf` | TLS برای client و inter-node |
| At-rest | TDE/backup encryption با محدودیت Edition | TDE هسته‌ای ندارد؛ filesystem/volume/cloud encryption | encrypted storage engine فقط Enterprise self-managed؛ Atlas encrypted |
| Auditing | server/database Audit؛ از 2016 SP1 همهٔ Editionها database audit | Logging هسته؛ audit غنی معمولاً pgAudit/سامانه بیرونی | facility رسمی auditing در Enterprise؛ Atlas M10+ |
| Row-level | RLS security policy | RLS policy | RLS عمومی معادل SQL ندارد؛ طراحی view/application |
| Column/field | column GRANT/DENY و Always Encrypted | column privileges و view | field encryption client/queryable؛ field ACL عمومی معادل column privilege نیست |
| Password policy | Windows policy برای SQL login قابل enforce | SCRAM و `VALID UNTIL`؛ complexity معمولاً بیرونی | SCRAM؛ policy گسترده وابسته به Atlas/IdP/فرایند |
| Network | endpoint/firewall/TLS | listen address، `pg_hba.conf`، firewall/TLS | `bindIp`، firewall، TLS و authentication restrictions |
| Backup security | encrypted backup در Editionهای پشتیبان | رمزنگاری فایل بیرونی | archive protection بیرونی؛ storage encryption بسته به Edition |

منابع رسمی: [SQL Server Audit](https://learn.microsoft.com/en-us/sql/relational-databases/security/auditing/sql-server-audit-database-engine)،
[SQL Server encryption](https://learn.microsoft.com/en-us/sql/relational-databases/security/encryption/sql-server-encryption)،
[SQL Server RLS](https://learn.microsoft.com/en-us/sql/relational-databases/security/row-level-security)،
[PostgreSQL authentication](https://www.postgresql.org/docs/16/auth-methods.html)،
[PostgreSQL TLS](https://www.postgresql.org/docs/16/ssl-tcp.html)،
[PostgreSQL privileges](https://www.postgresql.org/docs/16/ddl-priv.html)،
[PostgreSQL logging](https://www.postgresql.org/docs/16/runtime-config-logging.html)،
[MongoDB security checklist](https://www.mongodb.com/docs/manual/administration/security-checklist/)،
[MongoDB encryption at rest](https://www.mongodb.com/docs/manual/core/security-encryption-at-rest/) و
[MongoDB auditing](https://www.mongodb.com/docs/manual/core/auditing/).

## 19. مقایسهٔ effort توسعه

Rubric پیش‌ثبت‌شده در [developer_effort_rubric.md](developer_effort_rubric.md) هشت
معیار weighted دارد. Score باید پس از اجرای clean setup و ثبت diary تعیین شود؛
اعلام امتیاز اکنون ساختگی خواهد بود. Lines of code، تعداد فایل/دستور و مشکلات واقعی
به‌عنوان evidence گزارش می‌شوند، نه داوری پنهان. MongoDB Schema کوتاه‌تر است ولی
بخشی از Integrity به Loader منتقل شده؛ این انتقال باید در score relations منظور شود.

## 20. نتایج Benchmark

Benchmark واقعی با ۱۰۰٬۰۰۰ سفارش، Seed ثابت `20260830` و ۱۰ تکرار در هر Query
اجرا شد. اجرای موتور‌ها ترتیبی بود و خروجی خام ۹۶۰ ردیف دارد. به‌دلیل ARM بودن
Host، SQL Server با emulation و Docker با سقف ۴ GB اجرا شد؛ بنابراین اعداد واقعی
همین محیط‌اند و برای مقایسهٔ معماری x86-64 نهایی باید با احتیاط تفسیر شوند. جدول
اعداد در [measured_results.md](measured_results.md) و CSV خام در پوشهٔ `results`
ثبت شده است.

برای بازتولید یا تولید نسخهٔ جدید:

```bash
.venv/bin/python -m benchmark.validate_results
.venv/bin/python -m benchmark.analyze_results
```

فایل `measured_results.md` جدول واقعی Insert، میانگین indexed، Storage و برندهٔ هر
Query را تولید می‌کند. آن فایل باید در نسخهٔ تحویلی پس از آزمایش ضمیمه شود.

## 21. نمودارها

`benchmark.charts` نمودار Query، CPU، RAM، Storage و در صورت وجود Backup/Restore را
از CSV واقعی می‌سازد. نمودارهای Query، Insert، CPU، RAM، Storage و Backup/Restore
در پوشهٔ `charts` ثبت شده‌اند. Radar chart توصیهٔ اصلی نیست، چون normalize کردن
latency، security و effort می‌تواند تفاوت معنا و جهت مقیاس‌ها را پنهان کند؛ در صورت
استفاده باید normalization و «بیشتر بهتر/کمتر بهتر» صریح باشد.

## 22. بحث و تحلیل

تحلیل نهایی باید execution plan/`EXPLAIN`، تعداد row/document examined، hit ratio،
spill، serialization و network را کنار زمان بگذارد. به‌طور فرضیه‌ای JOIN optimizer،
WiredTiger document locality، MVCC، cache و index coverage می‌توانند تفاوت بسازند؛
اما هیچ‌کدام بدون plan/metric دلیل اثبات‌شده نیستند. اثر Index با نسبت زمان فاز دوم
به اول و هم‌زمان با افزایش `index_bytes` سنجیده می‌شود. Average تنها کافی نیست؛
Median و dispersion رفتار tail را روشن می‌کنند.

## 23. محدودیت‌ها

- یک Host و یک topology تک‌گره؛ نتایج قابل تعمیم به cluster نیستند.
- Dataset مصنوعی و حداکثر یک میلیون Order؛ skew واقعی کسب‌وکار ممکن است متفاوت باشد.
- Mongo embedding و SQL normalization مقایسهٔ Q05/Q13 را غیرمستقیم می‌کند.
- cold cache دقیق و portable نیست؛ فقط warm cache خودکار است.
- ابزار host-level منابع، مصرف خود process دیتابیس را جدا نمی‌کند.
- نسخه، Edition، config پیش‌فرض و resource limit روی نتیجه اثر دارند.
- SQL Server روی ARM emulation ناعادلانه است؛ x86-64 لازم است.
- Community در برابر Developer/Enterprise از نظر feature parity یکسان نیست.
- Backup formatها هم‌نوع نیستند.
- اجرای ترتیبی واحد اثر order و thermal drift را کاملاً حذف نمی‌کند.

## 24. نتیجه‌گیری

در این آزمایش SQL Server کمترین میانگین زمان Query و سریع‌ترین Backup/Restore را
داشت، PostgreSQL در بیشتر Queryهای مستقل برنده و از نظر هزینه، منابع و یکپارچگی
رابطه‌ای متعادل‌ترین گزینه بود، و MongoDB سریع‌ترین Insert و خواندن کامل Order را
ارائه کرد. برای همین سناریوی فروشگاه آنلاین PostgreSQL انتخاب کلی پیشنهادی است؛
SQL Server برای محیط‌های Microsoft/Enterprise و MongoDB برای workload واقعاً سندی
و کم‌وابسته به JOIN انتخاب مناسب‌تری هستند. این نتیجه فقط به محیط و workload ثبت‌شده
در `measured_results.md` مربوط است و تعمیم عمومی محسوب نمی‌شود.

## 25. منابع

1. Microsoft Learn, SQL Server 2022 editions, security, audit and encryption documentation.
2. PostgreSQL Global Development Group, PostgreSQL 16 documentation: roles, authentication, TLS, RLS and logging.
3. MongoDB Inc., MongoDB Manual: data modeling, security checklist, encryption and auditing.
4. اسکریپت‌ها، metadata و CSVهای همین مخزن به‌عنوان مواد بازتولید آزمایش.
