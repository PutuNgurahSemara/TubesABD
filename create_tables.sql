-- Drop tables if exist (untuk reset)
DROP TABLE IF EXISTS order_details CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS sellers CASCADE;

-- Tabel Sellers
CREATE TABLE sellers (
    seller_id VARCHAR(50) PRIMARY KEY,
    seller_name VARCHAR(255),
    seller_email VARCHAR(255),
    seller_phone VARCHAR(50),
    seller_region VARCHAR(50),
    seller_rating DECIMAL(3,2),
    join_date DATE
);

-- Tabel Customers
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(255),
    segment VARCHAR(50),
    country VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    region VARCHAR(50)
);

-- Tabel Products
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    category VARCHAR(100),
    sub_category VARCHAR(100),
    product_name VARCHAR(255)
);

-- Tabel Orders
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    order_date DATE,
    ship_date DATE,
    ship_mode VARCHAR(50),
    customer_id VARCHAR(50),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Tabel Order Details
CREATE TABLE order_details (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(50),
    product_id VARCHAR(50),
    seller_id VARCHAR(50),
    sales DECIMAL(10,2),
    quantity INTEGER,
    discount DECIMAL(5,2),
    profit DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
);
-- Index untuk optimasi query
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_order_details_order ON order_details(order_id);
CREATE INDEX idx_order_details_product ON order_details(product_id);
CREATE INDEX idx_order_details_seller ON order_details(seller_id);
CREATE INDEX idx_sellers_region ON sellers(seller_region);
CREATE INDEX idx_order_details_order ON order_details(order_id);
CREATE INDEX idx_order_details_product ON order_details(product_id);
