from __future__ import annotations

from datetime import datetime, timezone

SQLSERVER = {
    "q01_product_by_id": ("SELECT * FROM dbo.Products WHERE ProductId=?", (1,)),
    "q02_product_name": (
        "SELECT TOP (50) * FROM dbo.Products WHERE Name LIKE ? ORDER BY Name,ProductId",
        ("Product 0000001%",),
    ),
    "q03_products_by_category": (
        "SELECT ProductId,Sku,Name,Price,StockQuantity FROM dbo.Products WHERE CategoryId=? ORDER BY ProductId",
        (1,),
    ),
    "q04_orders_by_customer": (
        "SELECT OrderId,OrderDate,Status,TotalAmount FROM dbo.Orders WHERE CustomerId=? ORDER BY OrderDate DESC",
        (1,),
    ),
    "q05_complete_order": (
        """SELECT o.OrderId,o.OrderDate,o.Status,o.TotalAmount,c.CustomerId,c.Email,oi.OrderItemId,oi.Quantity,oi.LineTotal,p.ProductId,p.Name,pay.Method,pay.Status,s.Carrier,s.Status FROM dbo.Orders o JOIN dbo.Customers c ON c.CustomerId=o.CustomerId JOIN dbo.OrderItems oi ON oi.OrderId=o.OrderId JOIN dbo.Products p ON p.ProductId=oi.ProductId JOIN dbo.Payments pay ON pay.OrderId=o.OrderId JOIN dbo.Shipment s ON s.OrderId=o.OrderId WHERE o.OrderId=?""",
        (1,),
    ),
    "q06_total_sales": (
        "SELECT SUM(TotalAmount) FROM dbo.Orders WHERE Status<>'cancelled'",
        (),
    ),
    "q07_sales_date_range": (
        "SELECT SUM(TotalAmount) FROM dbo.Orders WHERE Status<>'cancelled' AND OrderDate>=? AND OrderDate<?",
        (datetime(2024, 1, 1), datetime(2025, 1, 1)),
    ),
    "q08_top_products": (
        """SELECT TOP (20) p.ProductId,p.Name,SUM(oi.Quantity) Units,SUM(oi.LineTotal) Revenue FROM dbo.OrderItems oi JOIN dbo.Orders o ON o.OrderId=oi.OrderId JOIN dbo.Products p ON p.ProductId=oi.ProductId WHERE o.Status<>'cancelled' GROUP BY p.ProductId,p.Name ORDER BY Units DESC,p.ProductId""",
        (),
    ),
    "q09_sales_by_category": (
        """SELECT c.CategoryId,c.Name,SUM(oi.LineTotal) Sales FROM dbo.Categories c JOIN dbo.Products p ON p.CategoryId=c.CategoryId JOIN dbo.OrderItems oi ON oi.ProductId=p.ProductId JOIN dbo.Orders o ON o.OrderId=oi.OrderId WHERE o.Status<>'cancelled' GROUP BY c.CategoryId,c.Name ORDER BY Sales DESC""",
        (),
    ),
    "q10_average_order_value": (
        "SELECT AVG(CAST(TotalAmount AS DECIMAL(18,2))) FROM dbo.Orders WHERE Status<>'cancelled'",
        (),
    ),
    "q11_orders_by_status": (
        "SELECT Status,COUNT_BIG(*) FROM dbo.Orders GROUP BY Status ORDER BY Status",
        (),
    ),
    "q12_top_customers": (
        """SELECT TOP (20) c.CustomerId,c.Email,SUM(o.TotalAmount) Spend FROM dbo.Customers c JOIN dbo.Orders o ON o.CustomerId=c.CustomerId WHERE o.Status<>'cancelled' GROUP BY c.CustomerId,c.Email ORDER BY Spend DESC,c.CustomerId""",
        (),
    ),
    "q13_heavy_multi_join": (
        """SELECT TOP (100) c.CustomerId,c.Email,cat.Name,COUNT(DISTINCT o.OrderId),SUM(oi.Quantity),SUM(oi.LineTotal),MAX(o.OrderDate) FROM dbo.Customers c JOIN dbo.Orders o ON o.CustomerId=c.CustomerId JOIN dbo.OrderItems oi ON oi.OrderId=o.OrderId JOIN dbo.Products p ON p.ProductId=oi.ProductId JOIN dbo.Categories cat ON cat.CategoryId=p.CategoryId JOIN dbo.Payments pay ON pay.OrderId=o.OrderId JOIN dbo.Shipment s ON s.OrderId=o.OrderId WHERE o.Status<>'cancelled' AND pay.Status IN ('paid','authorized') GROUP BY c.CustomerId,c.Email,cat.Name ORDER BY SUM(oi.LineTotal) DESC,c.CustomerId""",
        (),
    ),
}

POSTGRESQL = {
    "q01_product_by_id": ("SELECT * FROM products WHERE product_id=%s", (1,)),
    "q02_product_name": (
        "SELECT * FROM products WHERE name LIKE %s ORDER BY name,product_id LIMIT 50",
        ("Product 0000001%",),
    ),
    "q03_products_by_category": (
        "SELECT product_id,sku,name,price,stock_quantity FROM products WHERE category_id=%s ORDER BY product_id",
        (1,),
    ),
    "q04_orders_by_customer": (
        "SELECT order_id,order_date,status,total_amount FROM orders WHERE customer_id=%s ORDER BY order_date DESC",
        (1,),
    ),
    "q05_complete_order": (
        """SELECT o.order_id,o.order_date,o.status,o.total_amount,c.customer_id,c.email,oi.order_item_id,oi.quantity,oi.line_total,p.product_id,p.name,pay.method,pay.status,s.carrier,s.status FROM orders o JOIN customers c USING(customer_id) JOIN order_items oi USING(order_id) JOIN products p USING(product_id) JOIN payments pay USING(order_id) JOIN shipment s USING(order_id) WHERE o.order_id=%s""",
        (1,),
    ),
    "q06_total_sales": (
        "SELECT SUM(total_amount) FROM orders WHERE status<>'cancelled'",
        (),
    ),
    "q07_sales_date_range": (
        "SELECT SUM(total_amount) FROM orders WHERE status<>'cancelled' AND order_date>=%s AND order_date<%s",
        (
            datetime(2024, 1, 1, tzinfo=timezone.utc),
            datetime(2025, 1, 1, tzinfo=timezone.utc),
        ),
    ),
    "q08_top_products": (
        """SELECT p.product_id,p.name,SUM(oi.quantity) units,SUM(oi.line_total) revenue FROM order_items oi JOIN orders o USING(order_id) JOIN products p USING(product_id) WHERE o.status<>'cancelled' GROUP BY p.product_id,p.name ORDER BY units DESC,p.product_id LIMIT 20""",
        (),
    ),
    "q09_sales_by_category": (
        """SELECT c.category_id,c.name,SUM(oi.line_total) sales FROM categories c JOIN products p USING(category_id) JOIN order_items oi USING(product_id) JOIN orders o USING(order_id) WHERE o.status<>'cancelled' GROUP BY c.category_id,c.name ORDER BY sales DESC""",
        (),
    ),
    "q10_average_order_value": (
        "SELECT AVG(total_amount) FROM orders WHERE status<>'cancelled'",
        (),
    ),
    "q11_orders_by_status": (
        "SELECT status,COUNT(*) FROM orders GROUP BY status ORDER BY status",
        (),
    ),
    "q12_top_customers": (
        """SELECT c.customer_id,c.email,SUM(o.total_amount) spend FROM customers c JOIN orders o USING(customer_id) WHERE o.status<>'cancelled' GROUP BY c.customer_id,c.email ORDER BY spend DESC,c.customer_id LIMIT 20""",
        (),
    ),
    "q13_heavy_multi_join": (
        """SELECT c.customer_id,c.email,cat.name,COUNT(DISTINCT o.order_id),SUM(oi.quantity),SUM(oi.line_total),MAX(o.order_date) FROM customers c JOIN orders o USING(customer_id) JOIN order_items oi USING(order_id) JOIN products p USING(product_id) JOIN categories cat USING(category_id) JOIN payments pay USING(order_id) JOIN shipment s USING(order_id) WHERE o.status<>'cancelled' AND pay.status IN ('paid','authorized') GROUP BY c.customer_id,c.email,cat.name ORDER BY SUM(oi.line_total) DESC,c.customer_id LIMIT 100""",
        (),
    ),
}


def mongo_pipelines():
    start, end = (
        datetime(2024, 1, 1, tzinfo=timezone.utc),
        datetime(2025, 1, 1, tzinfo=timezone.utc),
    )
    return {
        "q01_product_by_id": ("find_product", {"_id": 1}),
        "q02_product_name": ("find_name", {"name": {"$regex": "^Product 0000001"}}),
        "q03_products_by_category": ("find_category", {"categoryId": 1}),
        "q04_orders_by_customer": ("find_customer_orders", {"customerId": 1}),
        "q05_complete_order": (
            "orders",
            [
                {"$match": {"_id": 1}},
                {
                    "$lookup": {
                        "from": "customers",
                        "localField": "customerId",
                        "foreignField": "_id",
                        "as": "customer",
                    }
                },
                {"$unwind": "$customer"},
            ],
        ),
        "q06_total_sales": (
            "orders",
            [
                {"$match": {"status": {"$ne": "cancelled"}}},
                {"$group": {"_id": None, "value": {"$sum": "$totalAmount"}}},
            ],
        ),
        "q07_sales_date_range": (
            "orders",
            [
                {
                    "$match": {
                        "status": {"$ne": "cancelled"},
                        "orderDate": {"$gte": start, "$lt": end},
                    }
                },
                {"$group": {"_id": None, "value": {"$sum": "$totalAmount"}}},
            ],
        ),
        "q08_top_products": (
            "orders",
            [
                {"$match": {"status": {"$ne": "cancelled"}}},
                {"$unwind": "$items"},
                {
                    "$group": {
                        "_id": {"id": "$items.productId", "name": "$items.productName"},
                        "units": {"$sum": "$items.quantity"},
                        "revenue": {"$sum": "$items.lineTotal"},
                    }
                },
                {"$sort": {"units": -1, "_id.id": 1}},
                {"$limit": 20},
            ],
        ),
        "q09_sales_by_category": (
            "orders",
            [
                {"$match": {"status": {"$ne": "cancelled"}}},
                {"$unwind": "$items"},
                {
                    "$lookup": {
                        "from": "products",
                        "localField": "items.productId",
                        "foreignField": "_id",
                        "as": "p",
                    }
                },
                {"$unwind": "$p"},
                {
                    "$lookup": {
                        "from": "categories",
                        "localField": "p.categoryId",
                        "foreignField": "_id",
                        "as": "c",
                    }
                },
                {"$unwind": "$c"},
                {
                    "$group": {
                        "_id": {"id": "$c._id", "name": "$c.name"},
                        "sales": {"$sum": "$items.lineTotal"},
                    }
                },
                {"$sort": {"sales": -1}},
            ],
        ),
        "q10_average_order_value": (
            "orders",
            [
                {"$match": {"status": {"$ne": "cancelled"}}},
                {"$group": {"_id": None, "value": {"$avg": "$totalAmount"}}},
            ],
        ),
        "q11_orders_by_status": (
            "orders",
            [
                {"$group": {"_id": "$status", "count": {"$sum": 1}}},
                {"$sort": {"_id": 1}},
            ],
        ),
        "q12_top_customers": (
            "orders",
            [
                {"$match": {"status": {"$ne": "cancelled"}}},
                {"$group": {"_id": "$customerId", "spend": {"$sum": "$totalAmount"}}},
                {"$sort": {"spend": -1, "_id": 1}},
                {"$limit": 20},
                {
                    "$lookup": {
                        "from": "customers",
                        "localField": "_id",
                        "foreignField": "_id",
                        "as": "customer",
                    }
                },
            ],
        ),
        "q13_heavy_multi_join": (
            "orders",
            [
                {
                    "$match": {
                        "status": {"$ne": "cancelled"},
                        "payment.status": {"$in": ["paid", "authorized"]},
                    }
                },
                {"$unwind": "$items"},
                {
                    "$lookup": {
                        "from": "products",
                        "localField": "items.productId",
                        "foreignField": "_id",
                        "as": "p",
                    }
                },
                {"$unwind": "$p"},
                {
                    "$lookup": {
                        "from": "categories",
                        "localField": "p.categoryId",
                        "foreignField": "_id",
                        "as": "c",
                    }
                },
                {"$unwind": "$c"},
                {
                    "$group": {
                        "_id": {"customerId": "$customerId", "category": "$c.name"},
                        "orders": {"$addToSet": "$_id"},
                        "units": {"$sum": "$items.quantity"},
                        "revenue": {"$sum": "$items.lineTotal"},
                        "lastOrder": {"$max": "$orderDate"},
                    }
                },
                {
                    "$lookup": {
                        "from": "customers",
                        "localField": "_id.customerId",
                        "foreignField": "_id",
                        "as": "customer",
                    }
                },
                {"$unwind": "$customer"},
                {
                    "$project": {
                        "email": "$customer.email",
                        "category": "$_id.category",
                        "ordersCount": {"$size": "$orders"},
                        "units": 1,
                        "revenue": 1,
                        "lastOrder": 1,
                    }
                },
                {"$sort": {"revenue": -1, "_id.customerId": 1}},
                {"$limit": 100},
            ],
        ),
    }
