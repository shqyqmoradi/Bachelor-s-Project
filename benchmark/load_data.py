from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict
from contextlib import closing
from dataclasses import asdict
from datetime import datetime, timezone
from decimal import Decimal

from bson import Decimal128
from bson.int64 import Int64

from .config import ROOT, Settings
from .data_generator import CanonicalGenerator
from .db import mongo_connect, postgres_connect, postgres_many, sqlserver_connect, sqlserver_many
from .monitor import SystemMonitor


def mssql_rows(rows):
    """Convert aware UTC datetimes to the naive value expected by DATETIME2."""
    return [tuple(v.astimezone(timezone.utc).replace(tzinfo=None) if isinstance(v, datetime) and v.tzinfo else v for v in row) for row in rows]


def load_sqlserver(s: Settings, g: CanonicalGenerator) -> dict:
    started = time.perf_counter()
    with SystemMonitor() as monitor, closing(sqlserver_connect(s)) as c:
        sqlserver_many(c, "INSERT dbo.Categories(CategoryId,Name,Description) VALUES(?,?,?)", g.categories())
        sqlserver_many(c, "INSERT dbo.Customers(CustomerId,FirstName,LastName,Email,Phone,CreatedAt,IsActive) VALUES(?,?,?,?,?,?,?)", mssql_rows(g.customers()))
        sqlserver_many(c, "INSERT dbo.Addresses(AddressId,CustomerId,Label,Line1,Line2,City,StateProvince,PostalCode,CountryCode,IsDefault) VALUES(?,?,?,?,?,?,?,?,?,?)", g.addresses())
        sqlserver_many(c, "INSERT dbo.Products(ProductId,CategoryId,Sku,Name,Description,Price,StockQuantity,IsActive,CreatedAt) VALUES(?,?,?,?,?,?,?,?,?)", mssql_rows(g.products()))
        c.commit()
        for b in g.order_batches():
            sqlserver_many(c, "INSERT dbo.Orders(OrderId,CustomerId,ShippingAddressId,OrderDate,Status,Currency,Subtotal,ShippingAmount,DiscountAmount) VALUES(?,?,?,?,?,?,?,?,?)", mssql_rows([r[:-1] for r in b.orders]))
            sqlserver_many(c, "INSERT dbo.OrderItems(OrderItemId,OrderId,ProductId,Quantity,UnitPrice,DiscountAmount) VALUES(?,?,?,?,?,?)", [r[:-1] for r in b.items])
            sqlserver_many(c, "INSERT dbo.Payments(PaymentId,OrderId,Method,Status,Amount,TransactionRef,PaidAt) VALUES(?,?,?,?,?,?,?)", mssql_rows(b.payments))
            sqlserver_many(c, "INSERT dbo.Shipment(ShipmentId,OrderId,Carrier,TrackingNumber,Status,ShippedAt,DeliveredAt) VALUES(?,?,?,?,?,?,?)", mssql_rows(b.shipments))
            c.commit()
    return result("sqlserver", s, started, monitor)


def load_postgresql(s: Settings, g: CanonicalGenerator) -> dict:
    started = time.perf_counter()
    with SystemMonitor() as monitor, postgres_connect(s) as c:
        postgres_many(c, "INSERT INTO categories(category_id,name,description) VALUES(%s,%s,%s)", g.categories())
        postgres_many(c, "INSERT INTO customers(customer_id,first_name,last_name,email,phone,created_at,is_active) VALUES(%s,%s,%s,%s,%s,%s,%s)", g.customers())
        postgres_many(c, "INSERT INTO addresses(address_id,customer_id,label,line1,line2,city,state_province,postal_code,country_code,is_default) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", g.addresses())
        postgres_many(c, "INSERT INTO products(product_id,category_id,sku,name,description,price,stock_quantity,is_active,created_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)", g.products())
        c.commit()
        for b in g.order_batches():
            postgres_many(c, "INSERT INTO orders(order_id,customer_id,shipping_address_id,order_date,status,currency,subtotal,shipping_amount,discount_amount) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)", [r[:-1] for r in b.orders])
            postgres_many(c, "INSERT INTO order_items(order_item_id,order_id,product_id,quantity,unit_price,discount_amount) VALUES(%s,%s,%s,%s,%s,%s)", [r[:-1] for r in b.items])
            postgres_many(c, "INSERT INTO payments(payment_id,order_id,method,status,amount,transaction_ref,paid_at) VALUES(%s,%s,%s,%s,%s,%s,%s)", b.payments)
            postgres_many(c, "INSERT INTO shipment(shipment_id,order_id,carrier,tracking_number,status,shipped_at,delivered_at) VALUES(%s,%s,%s,%s,%s,%s,%s)", b.shipments)
            c.commit()
    return result("postgresql", s, started, monitor)


def d128(value: Decimal) -> Decimal128:
    return Decimal128(value)


def load_mongodb(s: Settings, g: CanonicalGenerator) -> dict:
    started = time.perf_counter()
    with SystemMonitor() as monitor, mongo_connect(s) as client:
        db = client[s.mongo_database]
        customers, addresses = g.customers(), g.addresses()
        customer_docs = []
        for c, a in zip(customers, addresses):
            doc = g.mongo_customer(c, a)
            doc["_id"], doc["addresses"][0]["addressId"] = Int64(doc["_id"]), Int64(doc["addresses"][0]["addressId"])
            customer_docs.append(doc)
        for start in range(0, len(customer_docs), s.batch_size):
            db.customers.insert_many(customer_docs[start:start+s.batch_size], ordered=True)
        db.categories.insert_many([{"_id": c[0], "name": c[1], "description": c[2]} for c in g.categories()])
        products = [{"_id": Int64(p[0]), "categoryId": p[1], "sku": p[2], "name": p[3], "description": p[4], "price": d128(p[5]), "stockQuantity": p[6], "isActive": p[7], "createdAt": p[8]} for p in g.products()]
        for start in range(0, len(products), s.batch_size):
            db.products.insert_many(products[start:start+s.batch_size], ordered=True)
        for b in g.order_batches():
            items_by_order: dict[int, list[tuple]] = defaultdict(list)
            for item in b.items:
                items_by_order[item[1]].append(item)
            docs = []
            for o, p, sh in zip(b.orders, b.payments, b.shipments):
                doc = g.mongo_order(o, items_by_order[o[0]], p, sh)
                doc["_id"] = Int64(doc["_id"])
                doc["customerId"] = Int64(doc["customerId"])
                doc["shippingAddress"]["addressId"] = Int64(doc["shippingAddress"]["addressId"])
                for key in ("subtotal", "shippingAmount", "discountAmount", "totalAmount"):
                    doc[key] = d128(doc[key])
                for item in doc["items"]:
                    item["orderItemId"], item["productId"] = Int64(item["orderItemId"]), Int64(item["productId"])
                    for key in ("unitPrice", "discountAmount", "lineTotal"):
                        item[key] = d128(item[key])
                doc["payment"]["paymentId"] = Int64(doc["payment"]["paymentId"])
                doc["payment"]["amount"] = d128(doc["payment"]["amount"])
                doc["shipment"]["shipmentId"] = Int64(doc["shipment"]["shipmentId"])
                docs.append(doc)
            db.orders.insert_many(docs, ordered=True)
    return result("mongodb", s, started, monitor)


def result(database: str, s: Settings, started: float, monitor: SystemMonitor) -> dict:
    stats = monitor.stats()
    return {"database": database, "metric": "canonical_dataset_insert", "orders": s.orders, "customers": s.customer_count, "addresses": s.customer_count, "products": s.product_count, "elapsed_seconds": time.perf_counter() - started, **asdict(stats), "is_real": True}


def main() -> None:
    parser = argparse.ArgumentParser(description="Load the same canonical dataset into one or all databases.")
    parser.add_argument("--database", choices=("all", "sqlserver", "postgresql", "mongodb"), default="all")
    parser.add_argument("--orders", type=int)
    args = parser.parse_args()
    defaults = Settings()
    s = Settings(orders=args.orders or defaults.orders)
    loaders = {"sqlserver": load_sqlserver, "postgresql": load_postgresql, "mongodb": load_mongodb}
    results = []
    for name, loader in loaders.items():
        if args.database in ("all", name):
            print(f"Loading {name}: {s.orders:,} orders...")
            results.append(loader(s, CanonicalGenerator(s)))
    path = ROOT / "results" / "insert_results.json"
    path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote real measurements to {path}")


if __name__ == "__main__":
    main()
