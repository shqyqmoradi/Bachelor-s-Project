# ERD and cardinalities

```mermaid
erDiagram
    CUSTOMERS ||--o{ ADDRESSES : owns
    CUSTOMERS ||--o{ ORDERS : places
    ADDRESSES ||--o{ ORDERS : used_for_shipping
    CATEGORIES ||--o{ PRODUCTS : classifies
    ORDERS ||--|{ ORDER_ITEMS : contains
    PRODUCTS ||--o{ ORDER_ITEMS : appears_in
    ORDERS ||--|| PAYMENTS : has
    ORDERS ||--|| SHIPMENT : has

    CUSTOMERS { bigint CustomerId PK
      varchar Email UK
      varchar FirstName
      varchar LastName
      timestamp CreatedAt }
    ADDRESSES { bigint AddressId PK
      bigint CustomerId FK
      varchar City
      char CountryCode }
    CATEGORIES { int CategoryId PK
      varchar Name UK }
    PRODUCTS { bigint ProductId PK
      int CategoryId FK
      varchar Sku UK
      decimal Price
      int StockQuantity }
    ORDERS { bigint OrderId PK
      bigint CustomerId FK
      bigint ShippingAddressId FK
      timestamp OrderDate
      varchar Status
      decimal TotalAmount }
    ORDER_ITEMS { bigint OrderItemId PK
      bigint OrderId FK
      bigint ProductId FK
      smallint Quantity
      decimal UnitPrice }
    PAYMENTS { bigint PaymentId PK
      bigint OrderId FK_UK
      varchar Method
      varchar Status }
    SHIPMENT { bigint ShipmentId PK
      bigint OrderId FK_UK
      varchar TrackingNumber UK
      varchar Status }
```

`Payment` and `Shipment` are modeled as mandatory 1:1 records in the generated
dataset, with `pending` states representing work not yet completed. This avoids
null-related differences across the three workloads. A production system might
model multiple payment attempts and shipment packages as 1:N; that is deliberately
outside this controlled experiment.

## MongoDB document decisions

- `customers` embeds bounded addresses because they are owned by one customer and
  commonly read together. The canonical generator uses one address per customer.
- `orders` embeds immutable shipping-address snapshot, order items, payment and
  shipment. These components share the order lifecycle and are retrieved together.
- `products` and `categories` remain separate references because many orders reuse
  them and their current catalog data changes independently.
- Each embedded order item stores `productId`, historical `productName` and
  `unitPrice`. The ID permits cross-collection aggregation; the snapshot preserves
  invoice history.
- MongoDB lacks server-enforced foreign keys. The generator and loader enforce
  referential validity; validation rules enforce document shape and numeric types.

