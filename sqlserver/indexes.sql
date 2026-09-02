USE OnlineShopDB;
CREATE INDEX IX_Products_CategoryId ON dbo.Products(CategoryId) INCLUDE (Name, Price, StockQuantity);
CREATE INDEX IX_Products_Name ON dbo.Products(Name);
CREATE INDEX IX_Orders_Customer_Date ON dbo.Orders(CustomerId, OrderDate DESC) INCLUDE (Status, TotalAmount);
CREATE INDEX IX_Orders_OrderDate ON dbo.Orders(OrderDate) INCLUDE (Status, TotalAmount);
CREATE INDEX IX_Orders_Status ON dbo.Orders(Status);
CREATE INDEX IX_OrderItems_ProductId ON dbo.OrderItems(ProductId) INCLUDE (Quantity, LineTotal);
-- OrderId, Email, Payment.OrderId and Shipment.OrderId already have PK/UNIQUE indexes.

