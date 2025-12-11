-- ============================================
-- RESET
-- ============================================

DROP TABLE IF EXISTS order_details CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS subcategories CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS sellers CASCADE;

DROP TYPE IF EXISTS segment_enum;
DROP TYPE IF EXISTS region_enum;
DROP TYPE IF EXISTS ship_mode_enum;

-- ============================================
-- ENUM
-- ============================================

CREATE TYPE segment_enum AS ENUM ('Consumer', 'Corporate', 'Home Office');
CREATE TYPE region_enum AS ENUM ('East', 'West', 'Central', 'South');
CREATE TYPE ship_mode_enum AS ENUM ('First Class', 'Second Class', 'Standard Class', 'Same Day');

-- ============================================
-- TABLE STRUCTURE
-- ============================================

-- CATEGORY LEVEL 1
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

-- SUBCATEGORY LEVEL 2
CREATE TABLE subcategories (
    subcategory_id SERIAL PRIMARY KEY,
    category_id INT NOT NULL,
    subcategory_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- SELLERS
CREATE TABLE sellers (
    seller_id VARCHAR(50) PRIMARY KEY,
    seller_name VARCHAR(255) NOT NULL,
    seller_email VARCHAR(255) UNIQUE NOT NULL,
    seller_phone VARCHAR(20),
    seller_region region_enum,
    seller_rating DECIMAL(3,2),
    join_date DATE,
    CONSTRAINT chk_seller_rating CHECK (seller_rating BETWEEN 0 AND 5)
);

-- CUSTOMERS
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    segment segment_enum,
    country VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    region region_enum
);

-- PRODUCTS LEVEL 3
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    category_id INT NOT NULL,
    subcategory_id INT NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (subcategory_id) REFERENCES subcategories(subcategory_id)
);

-- ORDERS
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    order_date DATE NOT NULL,
    ship_date DATE,
    ship_mode ship_mode_enum,
    customer_id VARCHAR(50) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT chk_ship_date CHECK (ship_date >= order_date)
);

-- ORDER DETAILS
CREATE TABLE order_details (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    seller_id VARCHAR(50),
    sales DECIMAL(10,2) NOT NULL,
    quantity INTEGER NOT NULL,
    discount DECIMAL(5,2) DEFAULT 0,
    profit DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id),
    CONSTRAINT chk_quantity CHECK (quantity > 0),
    CONSTRAINT chk_discount CHECK (discount BETWEEN 0 AND 1),
    CONSTRAINT chk_sales CHECK (sales >= 0)
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_order_date ON orders(order_date);

CREATE INDEX idx_order_details_order ON order_details(order_id);
CREATE INDEX idx_order_details_product ON order_details(product_id);
CREATE INDEX idx_order_details_seller ON order_details(seller_id);

CREATE INDEX idx_sellers_region ON sellers(seller_region);

CREATE INDEX idx_customers_segment ON customers(segment);
CREATE INDEX idx_customers_region ON customers(region);

CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_subcategory ON products(subcategory_id);
