// Run: mongosh "$MONGO_URI" mongodb/schema.js
db = db.getSiblingDB("OnlineShopDB");

for (const name of ["customers", "categories", "products", "orders"]) {
  if (db.getCollectionNames().includes(name)) db[name].drop();
}

db.createCollection("customers", { validator: { $jsonSchema: {
  bsonType: "object", required: ["_id","firstName","lastName","email","createdAt","isActive","addresses"],
  properties: {
    _id: { bsonType: "long" }, email: { bsonType: "string" }, createdAt: { bsonType: "date" },
    addresses: { bsonType: "array", items: { bsonType: "object", required: ["addressId","label","line1","city","postalCode","countryCode","isDefault"] } }
  }
}}});

db.createCollection("categories", { validator: { $jsonSchema: {
  bsonType: "object", required: ["_id","name"], properties: { _id: { bsonType: "int" }, name: { bsonType: "string" } }
}}});

db.createCollection("products", { validator: { $jsonSchema: {
  bsonType: "object", required: ["_id","categoryId","sku","name","price","stockQuantity","isActive","createdAt"],
  properties: {
    _id: { bsonType: "long" }, categoryId: { bsonType: "int" }, price: { bsonType: "decimal" },
    stockQuantity: { bsonType: "int", minimum: 0 }, createdAt: { bsonType: "date" }
  }
}}});

db.createCollection("orders", { validator: { $jsonSchema: {
  bsonType: "object", required: ["_id","customerId","shippingAddress","orderDate","status","currency","subtotal","shippingAmount","discountAmount","totalAmount","items","payment","shipment"],
  properties: {
    _id: { bsonType: "long" }, customerId: { bsonType: "long" }, orderDate: { bsonType: "date" },
    status: { enum: ["pending","paid","processing","shipped","delivered","cancelled"] },
    currency: { enum: ["USD"] }, subtotal: { bsonType: "decimal" }, totalAmount: { bsonType: "decimal" },
    shippingAddress: { bsonType: "object", required: ["addressId","line1","city","postalCode","countryCode"] },
    items: { bsonType: "array", minItems: 1, items: { bsonType: "object", required: ["orderItemId","productId","productName","quantity","unitPrice","discountAmount","lineTotal"], properties: { orderItemId: {bsonType:"long"}, productId: {bsonType:"long"}, quantity: {bsonType:"int",minimum:1}, unitPrice: {bsonType:"decimal"}, lineTotal: {bsonType:"decimal"} } } },
    payment: { bsonType: "object", required: ["paymentId","method","status","amount","transactionRef"] },
    shipment: { bsonType: "object", required: ["shipmentId","status"] }
  }
}}});

// Mandatory logical constraints: these stay in both benchmark index phases.
db.customers.createIndex({email:1},{unique:true,name:"ux_customers_email"});
db.products.createIndex({sku:1},{unique:true,name:"ux_products_sku"});
db.orders.createIndex({"payment.transactionRef":1},{unique:true,name:"ux_payment_transaction_ref"});
db.orders.createIndex({"shipment.trackingNumber":1},{unique:true,name:"ux_shipment_tracking",partialFilterExpression:{"shipment.trackingNumber":{$type:"string"}}});

print("OnlineShopDB collections and validators created.");
