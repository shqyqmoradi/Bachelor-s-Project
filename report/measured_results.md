# نتایج اندازه‌گیری‌شده

> این فایل فقط از CSVهای دارای `is_real=true` تولید شده است.

## جدول نهایی معیارهای عددی

| metric                  |   sqlserver |   postgresql |   mongodb |
|:------------------------|------------:|-------------:|----------:|
| Insert Time (s)         |      27.139 |       27.587 |    11.423 |
| Average Query Time (ms) |      39.291 |       46.922 |  2046.804 |
| Minimum Query Time (ms) |       0.677 |        0.295 |     0.371 |
| Maximum Query Time (ms) |     404.818 |      591.441 | 20022.740 |
| Average CPU (%)         |       3.557 |        2.795 |     5.850 |
| Peak Host RAM (MiB)     |    3933.047 |     3669.609 |  3336.812 |
| Total Storage (MiB)     |     336.000 |      122.153 |    37.973 |
| Backup Time (s)         |       0.953 |        1.644 |     3.683 |
| Restore Time (s)        |       1.251 |        2.395 |     3.405 |

Developer Effort با rubric و diary امتیاز می‌گیرد و Security یک feature matrix است؛ تبدیل این دو به عدد بدون ارزیابی ثبت‌شده انجام نمی‌شود.

## میانگین هر Query در فاز indexed

| query_id                 |   mongodb |   postgresql |   sqlserver |
|:-------------------------|----------:|-------------:|------------:|
| q01_product_by_id        |     0.445 |        0.339 |       0.771 |
| q02_product_name         |     1.304 |        0.530 |       1.451 |
| q03_products_by_category |     8.034 |        0.697 |       2.404 |
| q04_orders_by_customer   |     0.598 |        0.368 |       0.995 |
| q05_complete_order       |     0.540 |        0.660 |       0.949 |
| q06_total_sales          |    84.877 |       10.901 |      23.508 |
| q07_sales_date_range     |    29.397 |        4.921 |       8.781 |
| q08_top_products         |   303.753 |       74.636 |      75.422 |
| q09_sales_by_category    | 12808.857 |       56.078 |      68.024 |
| q10_average_order_value  |    90.589 |       10.724 |      25.607 |
| q11_orders_by_status     |    30.681 |       10.655 |      15.390 |
| q12_top_customers        |   121.396 |       37.237 |      43.322 |
| q13_heavy_multi_join     | 19266.948 |      541.381 |     350.272 |
| q15_insert               |     0.491 |        0.773 |       8.421 |
| q16_update               |     0.518 |        0.523 |       1.814 |
| q17_delete               |     0.443 |        0.329 |       1.522 |

## برندهٔ مشاهده‌شده برای هر Query در فاز indexed

| Query | کمترین Average | زمان (ms) |
|---|---|---:|
| q01_product_by_id | postgresql | 0.339 |
| q02_product_name | postgresql | 0.530 |
| q03_products_by_category | postgresql | 0.697 |
| q04_orders_by_customer | postgresql | 0.368 |
| q05_complete_order | mongodb | 0.540 |
| q06_total_sales | postgresql | 10.901 |
| q07_sales_date_range | postgresql | 4.921 |
| q08_top_products | postgresql | 74.636 |
| q09_sales_by_category | postgresql | 56.078 |
| q10_average_order_value | postgresql | 10.724 |
| q11_orders_by_status | postgresql | 10.655 |
| q12_top_customers | postgresql | 37.237 |
| q13_heavy_multi_join | sqlserver | 350.272 |
| q15_insert | mongodb | 0.491 |
| q16_update | mongodb | 0.518 |
| q17_delete | postgresql | 0.329 |

این جدول علیت را ثابت نمی‌کند. برای توضیح تفاوت‌ها باید execution plan، تعداد اسناد/ردیف‌های بررسی‌شده، cache، serialization و overhead اتصال همراه نتایج بررسی شوند. Q05 و Q13 به‌علت تفاوت embedding/JOIN کاملاً هم‌ساخت نیستند.
