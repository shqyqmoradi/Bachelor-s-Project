db = db.getSiblingDB("OnlineShopDB");
const productId = NumberLong(1), categoryId = 1, customerId = NumberLong(1), orderId = NumberLong(1);
// Q01-Q04
db.products.findOne({_id: productId});
db.products.find({name: /^Product 1/}).sort({name:1,_id:1}).limit(50).toArray();
db.products.find({categoryId}).sort({_id:1}).toArray();
db.orders.find({customerId},{items:0,payment:0,shipment:0}).sort({orderDate:-1}).toArray();
// Q05: order embeds items/payment/shipment; customer lookup is still required.
db.orders.aggregate([{$match:{_id:orderId}},{$lookup:{from:"customers",localField:"customerId",foreignField:"_id",as:"customer"}},{$unwind:"$customer"}]).toArray();
// Q06-Q07
db.orders.aggregate([{$match:{status:{$ne:"cancelled"}}},{$group:{_id:null,totalSales:{$sum:"$totalAmount"}}}]).toArray();
db.orders.aggregate([{$match:{status:{$ne:"cancelled"},orderDate:{$gte:ISODate("2024-01-01"),$lt:ISODate("2025-01-01")}}},{$group:{_id:null,totalSales:{$sum:"$totalAmount"}}}]).toArray();
// Q08
db.orders.aggregate([{$match:{status:{$ne:"cancelled"}}},{$unwind:"$items"},{$group:{_id:{id:"$items.productId",name:"$items.productName"},units:{$sum:"$items.quantity"},revenue:{$sum:"$items.lineTotal"}}},{$sort:{units:-1,"_id.id":1}},{$limit:20}]).toArray();
// Q09
db.orders.aggregate([{$match:{status:{$ne:"cancelled"}}},{$unwind:"$items"},{$lookup:{from:"products",localField:"items.productId",foreignField:"_id",as:"product"}},{$unwind:"$product"},{$lookup:{from:"categories",localField:"product.categoryId",foreignField:"_id",as:"category"}},{$unwind:"$category"},{$group:{_id:{id:"$category._id",name:"$category.name"},sales:{$sum:"$items.lineTotal"}}},{$sort:{sales:-1}}]).toArray();
// Q10-Q12
db.orders.aggregate([{$match:{status:{$ne:"cancelled"}}},{$group:{_id:null,averageOrderValue:{$avg:"$totalAmount"}}}]).toArray();
db.orders.aggregate([{$group:{_id:"$status",orderCount:{$sum:1}}},{$sort:{_id:1}}]).toArray();
db.orders.aggregate([{$match:{status:{$ne:"cancelled"}}},{$group:{_id:"$customerId",spend:{$sum:"$totalAmount"}}},{$sort:{spend:-1,_id:1}},{$limit:20},{$lookup:{from:"customers",localField:"_id",foreignField:"_id",as:"customer"}},{$unwind:"$customer"}]).toArray();
// Q13: logical equivalent of the relational heavy multi-join.
db.orders.aggregate([{$match:{status:{$ne:"cancelled"},"payment.status":{$in:["paid","authorized"]}}},{$unwind:"$items"},{$lookup:{from:"products",localField:"items.productId",foreignField:"_id",as:"product"}},{$unwind:"$product"},{$lookup:{from:"categories",localField:"product.categoryId",foreignField:"_id",as:"category"}},{$unwind:"$category"},{$group:{_id:{customerId:"$customerId",category:"$category.name"},orders:{$addToSet:"$_id"},units:{$sum:"$items.quantity"},itemRevenue:{$sum:"$items.lineTotal"},lastOrder:{$max:"$orderDate"}}},{$lookup:{from:"customers",localField:"_id.customerId",foreignField:"_id",as:"customer"}},{$unwind:"$customer"},{$project:{email:"$customer.email",category:"$_id.category",ordersCount:{$size:"$orders"},units:1,itemRevenue:1,lastOrder:1}},{$sort:{itemRevenue:-1,"_id.customerId":1}},{$limit:100}]).toArray();
// Q14-Q16 are isolated by deleting the temporary document.
db.products.insertOne({_id:NumberLong(9000000001),categoryId:1,sku:"BENCH-1",name:"Benchmark Product",price:NumberDecimal("10.00"),stockQuantity:10,isActive:true,createdAt:new Date()});
db.products.updateOne({_id:NumberLong(9000000001)},{$inc:{stockQuantity:1}});
db.products.deleteOne({_id:NumberLong(9000000001)});
