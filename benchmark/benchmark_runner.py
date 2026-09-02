from __future__ import annotations

import statistics
import time
from contextlib import closing
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Callable

from bson import Decimal128
from bson.int64 import Int64

from .config import ROOT, Settings
from .db import execute_postgres_file, execute_tsql_file, mongo_connect, postgres_connect, sqlserver_connect
from .monitor import SystemMonitor
from .queries import POSTGRESQL, SQLSERVER, mongo_pipelines


def _record(database: str, phase: str, query_id: str, run: int, elapsed: float, monitor: SystemMonitor, count: int) -> dict:
    stats = monitor.stats()
    return {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "database": database, "index_phase": phase, "cache_mode": "warm", "query_id": query_id, "run": run, "elapsed_ms": elapsed * 1000, "result_rows": count, **asdict(stats), "is_real": True}


def _measure(database: str, phase: str, query_id: str, run: int, operation: Callable[[], int]) -> dict:
    with SystemMonitor() as monitor:
        start = time.perf_counter()
        count = operation()
        elapsed = time.perf_counter() - start
    return _record(database, phase, query_id, run, elapsed, monitor, count)


def configure_indexes(database: str, s: Settings, enabled: bool) -> None:
    file_name = "indexes.sql" if enabled else "drop_indexes.sql"
    if database == "sqlserver":
        with closing(sqlserver_connect(s)) as c:
            execute_tsql_file(c, ROOT / "sqlserver" / file_name)
    elif database == "postgresql":
        with postgres_connect(s) as c:
            execute_postgres_file(c, ROOT / "postgresql" / file_name)
    else:
        with mongo_connect(s) as client:
            db = client[s.mongo_database]
            for collection in (db.customers, db.products, db.orders):
                for idx in collection.list_indexes():
                    if idx["name"] != "_id_" and not idx["name"].startswith("ux_"):
                        collection.drop_index(idx["name"])
            if enabled:
                db.products.create_index("categoryId", name="ix_products_category")
                db.products.create_index("name", name="ix_products_name")
                db.orders.create_index([("customerId",1),("orderDate",-1)], name="ix_orders_customer_date")
                db.orders.create_index("orderDate", name="ix_orders_date")
                db.orders.create_index("status", name="ix_orders_status")
                db.orders.create_index("items.productId", name="ix_orders_item_product")


def relational_benchmark(database: str, phase: str, s: Settings) -> list[dict]:
    catalog = SQLSERVER if database == "sqlserver" else POSTGRESQL
    connect = sqlserver_connect if database == "sqlserver" else postgres_connect
    rows = []
    with closing(connect(s)) as c:
        for query_id, (sql, params) in catalog.items():
            # Untimed warm-up primes plans and cache consistently.
            cur = c.cursor().execute(sql, params)
            cur.fetchall()
            for run in range(1, s.repetitions + 1):
                def operation(sql=sql, params=params) -> int:
                    cursor = c.cursor().execute(sql, params)
                    return len(cursor.fetchall())
                rows.append(_measure(database, phase, query_id, run, operation))
        rows.extend(relational_mutations(database, phase, s, c))
    return rows


def relational_mutations(database: str, phase: str, s: Settings, c) -> list[dict]:
    marker = 9_000_000_001
    if database == "sqlserver":
        statements = {
            "q15_insert": ("INSERT dbo.Products(ProductId,CategoryId,Sku,Name,Price,StockQuantity,IsActive,CreatedAt) VALUES(?,1,?,'Benchmark Product',10,10,1,SYSUTCDATETIME())", (marker,"BENCH-1")),
            "q16_update": ("UPDATE dbo.Products SET StockQuantity=StockQuantity+1 WHERE ProductId=?", (1,)),
            "q17_delete": ("DELETE dbo.Products WHERE ProductId=?", (marker,)),
        }
        seed_sql = "INSERT dbo.Products(ProductId,CategoryId,Sku,Name,Price,StockQuantity,IsActive,CreatedAt) VALUES(?,1,?,'Benchmark Product',10,10,1,SYSUTCDATETIME())"
    else:
        statements = {
            "q15_insert": ("INSERT INTO products(product_id,category_id,sku,name,price,stock_quantity,is_active,created_at) VALUES(%s,1,%s,'Benchmark Product',10,10,TRUE,NOW())", (marker,"BENCH-1")),
            "q16_update": ("UPDATE products SET stock_quantity=stock_quantity+1 WHERE product_id=%s", (1,)),
            "q17_delete": ("DELETE FROM products WHERE product_id=%s", (marker,)),
        }
        seed_sql = "INSERT INTO products(product_id,category_id,sku,name,price,stock_quantity,is_active,created_at) VALUES(%s,1,%s,'Benchmark Product',10,10,TRUE,NOW())"
    rows = []
    for query_id, (sql, params) in statements.items():
        for run in range(1, s.repetitions + 1):
            if query_id == "q17_delete": c.cursor().execute(seed_sql, (marker, "BENCH-1"))
            def operation(sql=sql, params=params) -> int:
                cur = c.cursor().execute(sql, params)
                return max(cur.rowcount, 0)
            rows.append(_measure(database, phase, query_id, run, operation))
            c.rollback()
    return rows


def mongodb_benchmark(phase: str, s: Settings) -> list[dict]:
    rows = []
    with mongo_connect(s) as client:
        db = client[s.mongo_database]
        for query_id, (kind, value) in mongo_pipelines().items():
            def operation(kind=kind, value=value) -> int:
                if kind == "find_product": return 1 if db.products.find_one(value) else 0
                if kind == "find_name": return len(list(db.products.find(value).sort([("name",1),("_id",1)]).limit(50)))
                if kind == "find_category": return len(list(db.products.find(value).sort("_id",1)))
                if kind == "find_customer_orders": return len(list(db.orders.find(value,{"items":0,"payment":0,"shipment":0}).sort("orderDate",-1)))
                return len(list(db[kind].aggregate(value, allowDiskUse=True)))
            operation()
            for run in range(1, s.repetitions + 1): rows.append(_measure("mongodb", phase, query_id, run, operation))
        marker = Int64(9_000_000_001)
        base = {"_id":marker,"categoryId":1,"sku":"BENCH-1","name":"Benchmark Product","price":Decimal128("10.00"),"stockQuantity":10,"isActive":True,"createdAt":datetime.now(timezone.utc)}
        for query_id in ("q15_insert","q16_update","q17_delete"):
            for run in range(1, s.repetitions + 1):
                db.products.delete_one({"_id":marker})
                if query_id != "q15_insert": db.products.insert_one(base.copy())
                if query_id == "q15_insert": op = lambda: int(db.products.insert_one(base.copy()).acknowledged)
                elif query_id == "q16_update": op = lambda: db.products.update_one({"_id":marker},{"$inc":{"stockQuantity":1}}).modified_count
                else: op = lambda: db.products.delete_one({"_id":marker}).deleted_count
                rows.append(_measure("mongodb", phase, query_id, run, op))
                db.products.delete_one({"_id":marker})
    return rows


def storage_and_version(database: str, s: Settings) -> dict:
    if database == "sqlserver":
        with closing(sqlserver_connect(s)) as c:
            version = c.cursor().execute("SELECT CAST(SERVERPROPERTY('ProductVersion') AS VARCHAR(30))").fetchone()[0]
            data = c.cursor().execute("SELECT COALESCE(SUM(CASE WHEN index_id IN (0,1) THEN used_page_count ELSE 0 END)*8*1024,0), 0 FROM sys.dm_db_partition_stats").fetchone()
            index_bytes = c.cursor().execute("SELECT COALESCE(SUM(used_page_count)*8*1024,0) FROM sys.dm_db_partition_stats WHERE index_id>1").fetchone()[0]
            total = c.cursor().execute("SELECT SUM(size)*8*1024 FROM sys.database_files").fetchone()[0]
    elif database == "postgresql":
        with postgres_connect(s) as c:
            version = c.execute("SHOW server_version").fetchone()[0]
            total = c.execute("SELECT pg_database_size(current_database())").fetchone()[0]
            data = c.execute("SELECT COALESCE(SUM(pg_table_size(oid)),0),0 FROM pg_class WHERE relkind='r'").fetchone()
            index_bytes = c.execute("SELECT COALESCE(SUM(pg_indexes_size(oid)),0) FROM pg_class WHERE relkind='r'").fetchone()[0]
    else:
        with mongo_connect(s) as client:
            version = client.server_info()["version"]
            stats = client[s.mongo_database].command("dbStats", scale=1)
            data_bytes, index_bytes, total = (stats.get("dataSize",0), stats.get("indexSize",0), stats.get("storageSize",0)+stats.get("indexSize",0))
            return {"database":database,"version":str(version),"data_bytes":int(data_bytes),"index_bytes":int(index_bytes),"total_bytes":int(total),"is_real":True}
    return {"database":database,"version":str(version),"data_bytes":int(data[0]),"index_bytes":int(index_bytes),"total_bytes":int(total),"is_real":True}


def summarize(raw: list[dict]) -> list[dict]:
    groups = {}
    for row in raw: groups.setdefault((row["database"],row["index_phase"],row["query_id"]),[]).append(row["elapsed_ms"])
    return [{"database":db,"index_phase":phase,"query_id":qid,"runs":len(values),"average_ms":statistics.mean(values),"minimum_ms":min(values),"maximum_ms":max(values),"median_ms":statistics.median(values),"stddev_ms":statistics.stdev(values) if len(values)>1 else 0.0,"is_real":True} for (db,phase,qid),values in sorted(groups.items())]
