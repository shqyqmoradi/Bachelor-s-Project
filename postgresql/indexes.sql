CREATE INDEX ix_products_category_id ON products(category_id) INCLUDE (name, price, stock_quantity);
CREATE INDEX ix_products_name_pattern ON products(name varchar_pattern_ops);
CREATE INDEX ix_orders_customer_date ON orders(customer_id, order_date DESC) INCLUDE (status, total_amount);
CREATE INDEX ix_orders_order_date ON orders(order_date) INCLUDE (status, total_amount);
CREATE INDEX ix_orders_status ON orders(status);
CREATE INDEX ix_order_items_product_id ON order_items(product_id) INCLUDE (quantity, line_total);
-- PK/UNIQUE constraints already index order_id, email and the 1:1 foreign keys.

