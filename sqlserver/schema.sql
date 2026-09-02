IF DB_ID(N'OnlineShopDB') IS NULL CREATE DATABASE OnlineShopDB;
GO
USE OnlineShopDB;
GO

DROP TABLE IF EXISTS dbo.Shipment, dbo.Payments, dbo.OrderItems, dbo.Orders, dbo.Addresses, dbo.Products, dbo.Categories, dbo.Customers;
GO

CREATE TABLE dbo.Customers (
    CustomerId BIGINT NOT NULL PRIMARY KEY,
    FirstName NVARCHAR(80) NOT NULL,
    LastName NVARCHAR(80) NOT NULL,
    Email NVARCHAR(254) NOT NULL UNIQUE,
    Phone NVARCHAR(32) NULL,
    CreatedAt DATETIME2(3) NOT NULL,
    IsActive BIT NOT NULL CONSTRAINT DF_Customers_IsActive DEFAULT 1
);

CREATE TABLE dbo.Categories (
    CategoryId INT NOT NULL PRIMARY KEY,
    Name NVARCHAR(120) NOT NULL UNIQUE,
    Description NVARCHAR(500) NULL
);

CREATE TABLE dbo.Products (
    ProductId BIGINT NOT NULL PRIMARY KEY,
    CategoryId INT NOT NULL,
    Sku NVARCHAR(64) NOT NULL UNIQUE,
    Name NVARCHAR(200) NOT NULL,
    Description NVARCHAR(1000) NULL,
    Price DECIMAL(12,2) NOT NULL CHECK (Price >= 0),
    StockQuantity INT NOT NULL CHECK (StockQuantity >= 0),
    IsActive BIT NOT NULL CONSTRAINT DF_Products_IsActive DEFAULT 1,
    CreatedAt DATETIME2(3) NOT NULL,
    CONSTRAINT FK_Products_Categories FOREIGN KEY (CategoryId) REFERENCES dbo.Categories(CategoryId)
);

CREATE TABLE dbo.Addresses (
    AddressId BIGINT NOT NULL PRIMARY KEY,
    CustomerId BIGINT NOT NULL,
    Label NVARCHAR(40) NOT NULL,
    Line1 NVARCHAR(200) NOT NULL,
    Line2 NVARCHAR(200) NULL,
    City NVARCHAR(100) NOT NULL,
    StateProvince NVARCHAR(100) NULL,
    PostalCode NVARCHAR(20) NOT NULL,
    CountryCode CHAR(2) NOT NULL CHECK (CountryCode LIKE '[A-Z][A-Z]'),
    IsDefault BIT NOT NULL CONSTRAINT DF_Addresses_IsDefault DEFAULT 0,
    CONSTRAINT FK_Addresses_Customers FOREIGN KEY (CustomerId) REFERENCES dbo.Customers(CustomerId),
    CONSTRAINT UQ_Addresses_Customer_Label UNIQUE (CustomerId, Label)
);

CREATE TABLE dbo.Orders (
    OrderId BIGINT NOT NULL PRIMARY KEY,
    CustomerId BIGINT NOT NULL,
    ShippingAddressId BIGINT NOT NULL,
    OrderDate DATETIME2(3) NOT NULL,
    Status VARCHAR(20) NOT NULL CHECK (Status IN ('pending','paid','processing','shipped','delivered','cancelled')),
    Currency CHAR(3) NOT NULL CHECK (Currency = 'USD'),
    Subtotal DECIMAL(14,2) NOT NULL CHECK (Subtotal >= 0),
    ShippingAmount DECIMAL(12,2) NOT NULL CHECK (ShippingAmount >= 0),
    DiscountAmount DECIMAL(12,2) NOT NULL CHECK (DiscountAmount >= 0),
    TotalAmount AS (Subtotal + ShippingAmount - DiscountAmount) PERSISTED,
    CONSTRAINT FK_Orders_Customers FOREIGN KEY (CustomerId) REFERENCES dbo.Customers(CustomerId),
    CONSTRAINT FK_Orders_Addresses FOREIGN KEY (ShippingAddressId) REFERENCES dbo.Addresses(AddressId)
);

CREATE TABLE dbo.OrderItems (
    OrderItemId BIGINT NOT NULL PRIMARY KEY,
    OrderId BIGINT NOT NULL,
    ProductId BIGINT NOT NULL,
    Quantity SMALLINT NOT NULL CHECK (Quantity BETWEEN 1 AND 100),
    UnitPrice DECIMAL(12,2) NOT NULL CHECK (UnitPrice >= 0),
    DiscountAmount DECIMAL(12,2) NOT NULL CHECK (DiscountAmount >= 0),
    LineTotal AS (Quantity * UnitPrice - DiscountAmount) PERSISTED,
    CONSTRAINT FK_OrderItems_Orders FOREIGN KEY (OrderId) REFERENCES dbo.Orders(OrderId) ON DELETE CASCADE,
    CONSTRAINT FK_OrderItems_Products FOREIGN KEY (ProductId) REFERENCES dbo.Products(ProductId),
    CONSTRAINT UQ_OrderItems_Order_Product UNIQUE (OrderId, ProductId)
);

CREATE TABLE dbo.Payments (
    PaymentId BIGINT NOT NULL PRIMARY KEY,
    OrderId BIGINT NOT NULL UNIQUE,
    Method VARCHAR(20) NOT NULL CHECK (Method IN ('card','paypal','bank_transfer','cash_on_delivery')),
    Status VARCHAR(20) NOT NULL CHECK (Status IN ('pending','authorized','paid','failed','refunded')),
    Amount DECIMAL(14,2) NOT NULL CHECK (Amount >= 0),
    TransactionRef NVARCHAR(80) NOT NULL UNIQUE,
    PaidAt DATETIME2(3) NULL,
    CONSTRAINT FK_Payments_Orders FOREIGN KEY (OrderId) REFERENCES dbo.Orders(OrderId) ON DELETE CASCADE
);

CREATE TABLE dbo.Shipment (
    ShipmentId BIGINT NOT NULL PRIMARY KEY,
    OrderId BIGINT NOT NULL UNIQUE,
    Carrier NVARCHAR(80) NULL,
    TrackingNumber NVARCHAR(100) NULL,
    Status VARCHAR(20) NOT NULL CHECK (Status IN ('pending','packed','shipped','in_transit','delivered','returned')),
    ShippedAt DATETIME2(3) NULL,
    DeliveredAt DATETIME2(3) NULL,
    CHECK (DeliveredAt IS NULL OR ShippedAt IS NULL OR DeliveredAt >= ShippedAt),
    CONSTRAINT FK_Shipment_Orders FOREIGN KEY (OrderId) REFERENCES dbo.Orders(OrderId) ON DELETE CASCADE
);
CREATE UNIQUE INDEX UX_Shipment_TrackingNumber ON dbo.Shipment(TrackingNumber) WHERE TrackingNumber IS NOT NULL;
GO
