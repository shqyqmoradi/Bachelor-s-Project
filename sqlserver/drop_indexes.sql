USE OnlineShopDB;
DROP INDEX IF EXISTS IX_Products_CategoryId ON dbo.Products;
DROP INDEX IF EXISTS IX_Products_Name ON dbo.Products;
DROP INDEX IF EXISTS IX_Orders_Customer_Date ON dbo.Orders;
DROP INDEX IF EXISTS IX_Orders_OrderDate ON dbo.Orders;
DROP INDEX IF EXISTS IX_Orders_Status ON dbo.Orders;
DROP INDEX IF EXISTS IX_OrderItems_ProductId ON dbo.OrderItems;

