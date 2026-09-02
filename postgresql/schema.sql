-- Run while connected to OnlineShopDB (created by Docker or createdb).
DROP TABLE IF EXISTS shipment, payments, order_items, orders, addresses, products, categories, customers CASCADE;

CREATE TABLE customers (
    customer_id BIGINT PRIMARY KEY,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    phone VARCHAR(32),
    created_at TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    description VARCHAR(500)
);

CREATE TABLE products (
    product_id BIGINT PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES categories(category_id),
    sku VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    description VARCHAR(1000),
    price NUMERIC(12,2) NOT NULL CHECK (price >= 0),
    stock_quantity INTEGER NOT NULL CHECK (stock_quantity >= 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE addresses (
    address_id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(customer_id),
    label VARCHAR(40) NOT NULL,
    line1 VARCHAR(200) NOT NULL,
    line2 VARCHAR(200),
    city VARCHAR(100) NOT NULL,
    state_province VARCHAR(100),
    postal_code VARCHAR(20) NOT NULL,
    country_code CHAR(2) NOT NULL CHECK (country_code ~ '^[A-Z]{2}$'),
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (customer_id, label)
);

CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(customer_id),
    shipping_address_id BIGINT NOT NULL REFERENCES addresses(address_id),
    order_date TIMESTAMPTZ NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending','paid','processing','shipped','delivered','cancelled')),
    currency CHAR(3) NOT NULL CHECK (currency = 'USD'),
    subtotal NUMERIC(14,2) NOT NULL CHECK (subtotal >= 0),
    shipping_amount NUMERIC(12,2) NOT NULL CHECK (shipping_amount >= 0),
    discount_amount NUMERIC(12,2) NOT NULL CHECK (discount_amount >= 0),
    total_amount NUMERIC(14,2) GENERATED ALWAYS AS (subtotal + shipping_amount - discount_amount) STORED
);

CREATE TABLE order_items (
    order_item_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    quantity SMALLINT NOT NULL CHECK (quantity BETWEEN 1 AND 100),
    unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
    discount_amount NUMERIC(12,2) NOT NULL CHECK (discount_amount >= 0),
    line_total NUMERIC(14,2) GENERATED ALWAYS AS (quantity * unit_price - discount_amount) STORED,
    UNIQUE (order_id, product_id)
);

CREATE TABLE payments (
    payment_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL UNIQUE REFERENCES orders(order_id) ON DELETE CASCADE,
    method VARCHAR(20) NOT NULL CHECK (method IN ('card','paypal','bank_transfer','cash_on_delivery')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending','authorized','paid','failed','refunded')),
    amount NUMERIC(14,2) NOT NULL CHECK (amount >= 0),
    transaction_ref VARCHAR(80) NOT NULL UNIQUE,
    paid_at TIMESTAMPTZ
);

CREATE TABLE shipment (
    shipment_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL UNIQUE REFERENCES orders(order_id) ON DELETE CASCADE,
    carrier VARCHAR(80),
    tracking_number VARCHAR(100) UNIQUE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending','packed','shipped','in_transit','delivered','returned')),
    shipped_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    CHECK (delivered_at IS NULL OR shipped_at IS NULL OR delivered_at >= shipped_at)
);
