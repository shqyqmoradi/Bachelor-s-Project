-- Use psql variables, for example: -v product_id=1 -v search='Product 1'
-- Q01
SELECT * FROM products WHERE product_id = :product_id;
-- Q02
SELECT * FROM products WHERE name LIKE :'search' || '%' ORDER BY name,product_id LIMIT 50;
-- Q03
SELECT product_id,sku,name,price,stock_quantity FROM products WHERE category_id=:category_id ORDER BY product_id;
-- Q04
SELECT order_id,order_date,status,total_amount FROM orders WHERE customer_id=:customer_id ORDER BY order_date DESC;
-- Q05
SELECT o.order_id,o.order_date,o.status,o.total_amount,c.customer_id,c.first_name,c.last_name,c.email,
 oi.order_item_id,oi.quantity,oi.unit_price,oi.line_total,p.product_id,p.name product_name,
 pay.method,pay.status payment_status,s.carrier,s.status shipment_status,s.tracking_number
FROM orders o JOIN customers c USING(customer_id) JOIN order_items oi USING(order_id)
JOIN products p USING(product_id) JOIN payments pay USING(order_id) JOIN shipment s USING(order_id)
WHERE o.order_id=:order_id;
-- Q06
SELECT SUM(total_amount) total_sales FROM orders WHERE status<>'cancelled';
-- Q07
SELECT SUM(total_amount) total_sales FROM orders WHERE status<>'cancelled' AND order_date>='2024-01-01' AND order_date<'2025-01-01';
-- Q08
SELECT p.product_id,p.name,SUM(oi.quantity) units,SUM(oi.line_total) revenue FROM order_items oi
JOIN orders o USING(order_id) JOIN products p USING(product_id) WHERE o.status<>'cancelled'
GROUP BY p.product_id,p.name ORDER BY units DESC,p.product_id LIMIT 20;
-- Q09
SELECT c.category_id,c.name,SUM(oi.line_total) sales FROM categories c JOIN products p USING(category_id)
JOIN order_items oi USING(product_id) JOIN orders o USING(order_id) WHERE o.status<>'cancelled'
GROUP BY c.category_id,c.name ORDER BY sales DESC;
-- Q10
SELECT AVG(total_amount) average_order_value FROM orders WHERE status<>'cancelled';
-- Q11
SELECT status,COUNT(*) order_count FROM orders GROUP BY status ORDER BY status;
-- Q12
SELECT c.customer_id,c.email,SUM(o.total_amount) spend FROM customers c JOIN orders o USING(customer_id)
WHERE o.status<>'cancelled' GROUP BY c.customer_id,c.email ORDER BY spend DESC,c.customer_id LIMIT 20;
-- Q13 heavy multi-join
SELECT c.customer_id,c.email,cat.name category,COUNT(DISTINCT o.order_id) orders_count,
 SUM(oi.quantity) units,SUM(oi.line_total) item_revenue,MAX(o.order_date) last_order
FROM customers c JOIN orders o USING(customer_id) JOIN order_items oi USING(order_id)
JOIN products p USING(product_id) JOIN categories cat USING(category_id) JOIN payments pay USING(order_id)
JOIN shipment s USING(order_id) WHERE o.status<>'cancelled' AND pay.status IN ('paid','authorized')
GROUP BY c.customer_id,c.email,cat.name ORDER BY item_revenue DESC,c.customer_id LIMIT 100;
-- Q13 is the heavy multi-join / equivalent MongoDB aggregation.
-- Q14-Q16: rollback keeps the measured database unchanged.
BEGIN;
INSERT INTO products VALUES(9000000001,1,'BENCH-1','Benchmark Product',NULL,10,10,TRUE,NOW());
UPDATE products SET stock_quantity=stock_quantity+1 WHERE product_id=9000000001;
DELETE FROM products WHERE product_id=9000000001;
ROLLBACK;
