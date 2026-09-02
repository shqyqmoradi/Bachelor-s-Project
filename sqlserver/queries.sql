USE OnlineShopDB;
-- Parameters use sqlcmd variables: -v ProductId=1 CategoryId=1 CustomerId=1 OrderId=1 Search='Product 1'
-- Q01 product by ID
SELECT * FROM dbo.Products WHERE ProductId = $(ProductId);
-- Q02 product name prefix (indexable and identical semantics)
SELECT TOP (50) * FROM dbo.Products WHERE Name LIKE N'$(Search)%' ORDER BY Name, ProductId;
-- Q03 products in category
SELECT ProductId, Sku, Name, Price, StockQuantity FROM dbo.Products WHERE CategoryId=$(CategoryId) ORDER BY ProductId;
-- Q04 customer orders
SELECT OrderId, OrderDate, Status, TotalAmount FROM dbo.Orders WHERE CustomerId=$(CustomerId) ORDER BY OrderDate DESC;
-- Q05 complete order
SELECT o.OrderId,o.OrderDate,o.Status,o.TotalAmount,c.CustomerId,c.FirstName,c.LastName,c.Email,
       oi.OrderItemId,oi.Quantity,oi.UnitPrice,oi.LineTotal,p.ProductId,p.Name AS ProductName,
       pay.Method,pay.Status AS PaymentStatus,s.Carrier,s.Status AS ShipmentStatus,s.TrackingNumber
FROM dbo.Orders o JOIN dbo.Customers c ON c.CustomerId=o.CustomerId
JOIN dbo.OrderItems oi ON oi.OrderId=o.OrderId JOIN dbo.Products p ON p.ProductId=oi.ProductId
JOIN dbo.Payments pay ON pay.OrderId=o.OrderId JOIN dbo.Shipment s ON s.OrderId=o.OrderId
WHERE o.OrderId=$(OrderId);
-- Q06 total sales (exclude cancelled/failed)
SELECT SUM(TotalAmount) AS TotalSales FROM dbo.Orders WHERE Status <> 'cancelled';
-- Q07 total sales range
SELECT SUM(TotalAmount) AS TotalSales FROM dbo.Orders WHERE Status<>'cancelled' AND OrderDate >= '2024-01-01' AND OrderDate < '2025-01-01';
-- Q08 top-selling products
SELECT TOP (20) p.ProductId,p.Name,SUM(oi.Quantity) Units,SUM(oi.LineTotal) Revenue
FROM dbo.OrderItems oi JOIN dbo.Orders o ON o.OrderId=oi.OrderId JOIN dbo.Products p ON p.ProductId=oi.ProductId
WHERE o.Status<>'cancelled' GROUP BY p.ProductId,p.Name ORDER BY Units DESC,p.ProductId;
-- Q09 sales by category
SELECT c.CategoryId,c.Name,SUM(oi.LineTotal) Sales FROM dbo.Categories c JOIN dbo.Products p ON p.CategoryId=c.CategoryId
JOIN dbo.OrderItems oi ON oi.ProductId=p.ProductId JOIN dbo.Orders o ON o.OrderId=oi.OrderId
WHERE o.Status<>'cancelled' GROUP BY c.CategoryId,c.Name ORDER BY Sales DESC;
-- Q10 average order value
SELECT AVG(CAST(TotalAmount AS DECIMAL(18,2))) AverageOrderValue FROM dbo.Orders WHERE Status<>'cancelled';
-- Q11 order count by status
SELECT Status,COUNT_BIG(*) OrderCount FROM dbo.Orders GROUP BY Status ORDER BY Status;
-- Q12 highest-spending customers
SELECT TOP (20) c.CustomerId,c.Email,SUM(o.TotalAmount) Spend FROM dbo.Customers c JOIN dbo.Orders o ON o.CustomerId=c.CustomerId
WHERE o.Status<>'cancelled' GROUP BY c.CustomerId,c.Email ORDER BY Spend DESC,c.CustomerId;
-- Q13 heavy multi-join aggregate
SELECT TOP (100) c.CustomerId,c.Email,cat.Name Category,COUNT(DISTINCT o.OrderId) OrdersCount,
       SUM(oi.Quantity) Units,SUM(oi.LineTotal) ItemRevenue,MAX(o.OrderDate) LastOrder
FROM dbo.Customers c JOIN dbo.Orders o ON o.CustomerId=c.CustomerId JOIN dbo.OrderItems oi ON oi.OrderId=o.OrderId
JOIN dbo.Products p ON p.ProductId=oi.ProductId JOIN dbo.Categories cat ON cat.CategoryId=p.CategoryId
JOIN dbo.Payments pay ON pay.OrderId=o.OrderId JOIN dbo.Shipment s ON s.OrderId=o.OrderId
WHERE o.Status<>'cancelled' AND pay.Status IN ('paid','authorized')
GROUP BY c.CustomerId,c.Email,cat.Name ORDER BY ItemRevenue DESC,c.CustomerId;
-- Q14 is the Mongo aggregation equivalent of Q13; see mongodb/queries.js.
-- Q15/Q16/Q17 mutation tests must run in one transaction and roll back.
BEGIN TRAN;
INSERT dbo.Products(ProductId,CategoryId,Sku,Name,Price,StockQuantity,IsActive,CreatedAt) VALUES(9000000001,1,'BENCH-1','Benchmark Product',10,10,1,SYSUTCDATETIME());
UPDATE dbo.Products SET StockQuantity=StockQuantity+1 WHERE ProductId=9000000001;
DELETE dbo.Products WHERE ProductId=9000000001;
ROLLBACK;

