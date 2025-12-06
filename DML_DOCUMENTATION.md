# 📝 DML (Data Manipulation Language) Documentation - Superstore Application

## 📊 Overview

Dokumen ini menjelaskan semua operasi DML (SELECT, INSERT, UPDATE, DELETE) yang digunakan dalam aplikasi Superstore Dashboard. DML adalah bagian dari SQL yang digunakan untuk memanipulasi data dalam database.

---

## 🔍 SELECT Operations

### 1. Load All Data (Main Query)

**Lokasi:** `config.py` - fungsi `load_data()`

```sql
SELECT 
    o.order_id,
    o.order_date, 
    o.ship_date,
    o.ship_mode,
    c.customer_id,
    c.customer_name, 
    c.segment,
    c.country,
    c.city,
    c.state,
    c.postal_code,
    c.region,
    p.product_id,
    p.category, 
    p.sub_category, 
    p.product_name,
    s.seller_id,
    s.seller_name,
    s.seller_region,
    s.seller_rating,
    d.quantity, 
    d.sales, 
    d.discount, 
    d.profit
FROM order_details d
INNER JOIN orders o ON d.order_id = o.order_id
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN products p ON d.product_id = p.product_id
INNER JOIN sellers s ON d.seller_id = s.seller_id
ORDER BY o.order_date DESC;
```

**Penjelasan:**
- **Tujuan:** Mengambil semua data transaksi lengkap dengan informasi order, customer, product, dan seller
- **JOIN Operations:** 
  - `INNER JOIN orders`: Menggabungkan order_details dengan orders berdasarkan order_id
  - `INNER JOIN customers`: Menggabungkan dengan customers berdasarkan customer_id
  - `INNER JOIN products`: Menggabungkan dengan products berdasarkan product_id
  - `INNER JOIN sellers`: Menggabungkan dengan sellers berdasarkan seller_id
- **ORDER BY:** Mengurutkan berdasarkan tanggal order terbaru
- **Penggunaan:** Dashboard utama, semua analisis data

---

### 2. Sales by Category

**Lokasi:** `config.py` - fungsi `get_sales_by_category()`

```sql
SELECT 
    p.category,
    COUNT(d.id) as total_orders,
    SUM(d.quantity) as total_quantity,
    SUM(d.sales) as total_sales,
    SUM(d.profit) as total_profit,
    AVG(d.sales) as avg_sales
FROM order_details d
INNER JOIN products p ON d.product_id = p.product_id
GROUP BY p.category
ORDER BY total_sales DESC;
```

**Penjelasan:**
- **Tujuan:** Menghitung total penjualan per kategori produk
- **Aggregate Functions:**
  - `COUNT(d.id)`: Menghitung jumlah transaksi
  - `SUM(d.quantity)`: Total quantity terjual
  - `SUM(d.sales)`: Total nilai penjualan
  - `SUM(d.profit)`: Total profit
  - `AVG(d.sales)`: Rata-rata penjualan per transaksi
- **GROUP BY:** Mengelompokkan data berdasarkan kategori
- **ORDER BY:** Mengurutkan dari sales tertinggi
- **Penggunaan:** Analisis performa kategori produk

---

### 3. Sales by Segment

**Lokasi:** `config.py` - fungsi `get_sales_by_segment()`

```sql
SELECT 
    c.segment,
    COUNT(DISTINCT o.order_id) as total_orders,
    COUNT(DISTINCT c.customer_id) as total_customers,
    SUM(d.sales) as total_sales,
    SUM(d.profit) as total_profit
FROM order_details d
INNER JOIN orders o ON d.order_id = o.order_id
INNER JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.segment
ORDER BY total_sales DESC;
```

**Penjelasan:**
- **Tujuan:** Analisis penjualan per segment customer (Consumer, Corporate, Home Office)
- **DISTINCT:** Menghitung unique orders dan customers
- **Aggregate Functions:**
  - `COUNT(DISTINCT o.order_id)`: Jumlah order unik
  - `COUNT(DISTINCT c.customer_id)`: Jumlah customer unik
  - `SUM(d.sales)`: Total penjualan
  - `SUM(d.profit)`: Total profit
- **GROUP BY:** Berdasarkan segment customer
- **Penggunaan:** Analisis performa per segment pasar

---

### 4. Top Products

**Lokasi:** `config.py` - fungsi `get_top_products(limit=10)`

```sql
SELECT 
    p.product_name,
    p.category,
    p.sub_category,
    COUNT(d.id) as order_count,
    SUM(d.quantity) as total_quantity,
    SUM(d.sales) as total_sales,
    SUM(d.profit) as total_profit
FROM order_details d
INNER JOIN products p ON d.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category, p.sub_category
ORDER BY total_sales DESC
LIMIT 10;
```

**Penjelasan:**
- **Tujuan:** Menampilkan produk terlaris
- **GROUP BY:** Multiple columns (product_id, product_name, category, sub_category)
- **LIMIT:** Membatasi hasil hanya 10 produk teratas
- **Parameter:** `limit` bisa disesuaikan (default 10)
- **Penggunaan:** Dashboard top performers, analisis produk

---

### 5. Top Customers

**Lokasi:** `config.py` - fungsi `get_top_customers(limit=10)`

```sql
SELECT 
    c.customer_name,
    c.segment,
    c.region,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(d.sales) as total_sales,
    SUM(d.profit) as total_profit,
    AVG(d.sales) as avg_order_value
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
INNER JOIN order_details d ON o.order_id = d.order_id
GROUP BY c.customer_id, c.customer_name, c.segment, c.region
ORDER BY total_sales DESC
LIMIT 10;
```

**Penjelasan:**
- **Tujuan:** Identifikasi customer dengan pembelian tertinggi
- **AVG(d.sales):** Rata-rata nilai per order (Average Order Value)
- **GROUP BY:** Berdasarkan customer unique
- **LIMIT:** Top 10 customers
- **Penggunaan:** Customer retention analysis, VIP customer identification

---

### 6. Sales Trend Monthly

**Lokasi:** `config.py` - fungsi `get_sales_trend_monthly()`

```sql
SELECT 
    DATE_TRUNC('month', o.order_date) as month,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(d.sales) as total_sales,
    SUM(d.profit) as total_profit,
    AVG(d.sales) as avg_sales
FROM order_details d
INNER JOIN orders o ON d.order_id = o.order_id
GROUP BY DATE_TRUNC('month', o.order_date)
ORDER BY month;
```

**Penjelasan:**
- **Tujuan:** Trend penjualan per bulan untuk time series analysis
- **DATE_TRUNC('month', o.order_date):** Memotong tanggal ke awal bulan
  - Contoh: '2017-03-15' → '2017-03-01'
- **GROUP BY:** Berdasarkan bulan
- **ORDER BY month:** Urutan kronologis
- **Penggunaan:** Line chart, trend analysis, forecasting

---

### 7. Top Sellers

**Lokasi:** `config.py` - fungsi `get_top_sellers(limit=10)`

```sql
SELECT 
    s.seller_name,
    s.seller_region,
    s.seller_rating,
    COUNT(d.id) as total_orders,
    SUM(d.quantity) as total_quantity,
    SUM(d.sales) as total_sales,
    SUM(d.profit) as total_profit,
    ROUND(AVG(d.profit), 2) as avg_profit_per_order
FROM order_details d
INNER JOIN sellers s ON d.seller_id = s.seller_id
GROUP BY s.seller_id, s.seller_name, s.seller_region, s.seller_rating
ORDER BY total_sales DESC
LIMIT 10;
```

**Penjelasan:**
- **Tujuan:** Ranking seller berdasarkan performa
- **ROUND(AVG(d.profit), 2):** Rata-rata profit per order, dibulatkan 2 desimal
- **GROUP BY:** Seller unique dengan atributnya
- **Penggunaan:** Seller Analytics, commission calculation

---

### 8. Seller Performance

**Lokasi:** `config.py` - fungsi `get_seller_performance()`

```sql
SELECT 
    s.seller_name,
    s.seller_rating,
    SUM(d.sales) as total_sales,
    SUM(d.profit) as total_profit,
    COUNT(d.id) as total_orders
FROM order_details d
INNER JOIN sellers s ON d.seller_id = s.seller_id
GROUP BY s.seller_id, s.seller_name, s.seller_rating
ORDER BY s.seller_rating DESC;
```

**Penjelasan:**
- **Tujuan:** Analisis korelasi rating seller dengan performa penjualan
- **ORDER BY seller_rating DESC:** Urut berdasarkan rating tertinggi
- **Penggunaan:** Scatter plot Rating vs Profit, quality analysis

---

### 9. Profit by Category

**Lokasi:** `config.py` - fungsi `get_profit_by_category()`

```sql
SELECT 
    p.category,
    SUM(d.profit) as total_profit,
    SUM(CASE WHEN d.profit > 0 THEN d.profit ELSE 0 END) as positive_profit,
    SUM(CASE WHEN d.profit < 0 THEN d.profit ELSE 0 END) as negative_profit,
    COUNT(d.id) as order_count
FROM order_details d
INNER JOIN products p ON d.product_id = p.product_id
GROUP BY p.category
ORDER BY total_profit DESC;
```

**Penjelasan:**
- **Tujuan:** Analisis profitabilitas per kategori dengan breakdown untung/rugi
- **CASE Statement:**
  - `CASE WHEN d.profit > 0 THEN d.profit ELSE 0 END`: Hanya hitung profit positif
  - `CASE WHEN d.profit < 0 THEN d.profit ELSE 0 END`: Hanya hitung profit negatif
- **Penggunaan:** Stacked bar chart, profit analysis, loss identification

---

## ➕ INSERT Operations

### 1. Insert Customers

**Lokasi:** `config.py` - fungsi `add_data()`

```python
cur.execute("""
    INSERT INTO customers (customer_id, customer_name, segment, country, city, state, postal_code, region)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (customer_id) DO NOTHING;
""", tuple(row))
```

**Penjelasan:**
- **Tujuan:** Insert data customer dari Excel ke database
- **ON CONFLICT (customer_id) DO NOTHING:** 
  - Jika customer_id sudah ada (duplicate), skip insert
  - Mencegah error duplicate key
  - Idempotent operation (aman dijalankan berulang kali)
- **Parameterized Query:** Menggunakan `%s` placeholder untuk security (prevent SQL injection)
- **tuple(row):** Convert pandas row ke tuple untuk parameter binding

---

### 2. Insert Products

```python
cur.execute("""
    INSERT INTO products (product_id, category, sub_category, product_name)
    VALUES (%s,%s,%s,%s)
    ON CONFLICT (product_id) DO NOTHING;
""", tuple(row))
```

**Penjelasan:**
- **Tujuan:** Insert data produk
- **ON CONFLICT:** Duplicate handling untuk product_id
- **Kolom:** product_id (PK), category, sub_category, product_name

---

### 3. Insert Orders

```python
cur.execute("""
    INSERT INTO orders (order_id, order_date, ship_date, ship_mode, customer_id)
    VALUES (%s,%s,%s,%s,%s)
    ON CONFLICT (order_id) DO NOTHING;
""", tuple(row))
```

**Penjelasan:**
- **Tujuan:** Insert data order header
- **Foreign Key:** customer_id referensi ke customers table
- **ON CONFLICT:** Duplicate handling untuk order_id
- **Date Columns:** order_date, ship_date (DATE type)

---

### 4. Insert Order Details

```python
cur.execute("""
    INSERT INTO order_details (order_id, product_id, sales, quantity, discount, profit)
    VALUES (%s,%s,%s,%s,%s,%s)
""", (
    row["Order ID"],
    row["Product ID"],
    row["Sales"],
    row["Quantity"],
    row["Discount"],
    row["Profit"]
))
```

**Penjelasan:**
- **Tujuan:** Insert detail transaksi
- **TIDAK ADA ON CONFLICT:** 
  - Setiap baris order_details adalah unique (id SERIAL)
  - Bisa multiple items per order
- **Foreign Keys:**
  - order_id → orders
  - product_id → products
- **Transactional Data:** sales, quantity, discount, profit

---

## 🔄 Transaction Management

### Commit Pattern

```python
conn.commit()
```

**Penjelasan:**
- **Lokasi:** Setelah selesai semua INSERT operations
- **Tujuan:** Menyimpan semua perubahan ke database secara permanen
- **Transaction ACID:**
  - **Atomicity:** Semua INSERT sukses atau semua gagal (rollback)
  - **Consistency:** Data konsisten dengan constraints
  - **Isolation:** Transaksi terisolasi dari transaksi lain
  - **Durability:** Data permanen setelah commit

---

## 📊 Data Processing Flow

### 1. ETL Process (Extract, Transform, Load)

```python
def add_data():
    cur = conn.cursor()
    
    # EXTRACT
    df = pd.read_excel('Superstore.xls').head(500)
    
    # TRANSFORM
    customers = df[["Customer ID", "Customer Name", ...]].drop_duplicates()
    products = df[["Product ID", "Category", ...]].drop_duplicates()
    orders = df[["Order ID", "Order Date", ...]].drop_duplicates()
    
    # LOAD
    for _, row in customers.iterrows():
        cur.execute("INSERT INTO customers ...")
    
    conn.commit()
```

**Penjelasan:**
1. **Extract:** Baca data dari Excel (500 rows)
2. **Transform:** 
   - Drop duplicates untuk dimension tables (customers, products, orders)
   - Preserve all rows untuk fact table (order_details)
3. **Load:** Insert ke database dengan proper order (parent tables first)

---

## 🎯 Query Optimization Techniques

### 1. Index Usage

**Queries yang menggunakan indexes:**

```sql
-- Index pada foreign keys
WHERE d.order_id = o.order_id  -- idx_order_details_order_id
WHERE o.customer_id = c.customer_id  -- idx_orders_customer_id
WHERE d.product_id = p.product_id  -- idx_order_details_product_id

-- Index pada filter columns
WHERE p.category = 'Furniture'  -- idx_products_category
WHERE c.region = 'East'  -- idx_customers_region
WHERE o.order_date BETWEEN '2017-01-01' AND '2017-12-31'  -- idx_orders_order_date
```

---

### 2. Aggregate Functions

**Summary functions yang digunakan:**

| Function | Usage | Contoh |
|----------|-------|--------|
| `COUNT()` | Menghitung jumlah rows | `COUNT(d.id)` |
| `COUNT(DISTINCT)` | Menghitung unique values | `COUNT(DISTINCT o.order_id)` |
| `SUM()` | Total nilai | `SUM(d.sales)`, `SUM(d.profit)` |
| `AVG()` | Rata-rata | `AVG(d.sales)` |
| `ROUND()` | Pembulatan | `ROUND(AVG(d.profit), 2)` |
| `DATE_TRUNC()` | Truncate date | `DATE_TRUNC('month', o.order_date)` |

---

### 3. CASE Statements

**Conditional logic dalam query:**

```sql
-- Memisahkan profit positif dan negatif
SUM(CASE WHEN d.profit > 0 THEN d.profit ELSE 0 END) as positive_profit
SUM(CASE WHEN d.profit < 0 THEN d.profit ELSE 0 END) as negative_profit
```

**Kegunaan:**
- Filtering conditional dalam agregasi
- Pivot data tanpa subquery
- Business logic di SQL level

---

## 📈 Query Performance Metrics

### Execution Plan Analysis

**Best Practices:**

1. **EXPLAIN ANALYZE** untuk cek performance
```sql
EXPLAIN ANALYZE
SELECT * FROM order_details d
INNER JOIN orders o ON d.order_id = o.order_id;
```

2. **Index Scan vs Seq Scan**
   - ✅ Index Scan: Fast (O(log n))
   - ❌ Sequential Scan: Slow (O(n))

3. **Join Order Optimization**
   - PostgreSQL optimizer menentukan join order
   - Indexes membantu optimizer memilih strategi terbaik

---

## 🔒 Security Considerations

### 1. SQL Injection Prevention

**✅ Safe (Parameterized Query):**
```python
cur.execute("""
    INSERT INTO customers (customer_id, customer_name)
    VALUES (%s, %s)
""", (customer_id, customer_name))
```

**❌ Unsafe (String Concatenation):**
```python
# DON'T DO THIS!
cur.execute(f"INSERT INTO customers VALUES ('{customer_id}', '{customer_name}')")
```

---

### 2. Transaction Isolation

**Default Level:** READ COMMITTED
- Setiap query melihat data yang sudah di-commit
- Mencegah dirty reads
- Balance antara consistency dan performance

---

## 📝 Summary

### DML Operations dalam Aplikasi:

| Operation | Jumlah Query | Tables Involved | Complexity |
|-----------|--------------|-----------------|------------|
| **SELECT** | 9 queries | 5 tables | JOIN, GROUP BY, Aggregates |
| **INSERT** | 4 types | 4 tables | Batch insert, Conflict handling |
| **UPDATE** | 0 | - | Not used |
| **DELETE** | 0 | - | Not used (manual via SQL) |

### Key Features:

1. **Multi-table JOINs:** Up to 5 tables joined
2. **Aggregation:** COUNT, SUM, AVG, ROUND
3. **Date Functions:** DATE_TRUNC for time series
4. **Conditional Logic:** CASE statements
5. **Security:** Parameterized queries
6. **Performance:** Index usage, query optimization
7. **Data Integrity:** ON CONFLICT handling, transactions

---

## 🔗 Related Files

- `config.py` - All DML queries
- `app.py` / `app_streamlit.py` - Frontend using the queries
- `create_tables.sql` - DDL (table structure)
- `create_indexes.sql` - Index definitions
- `INDEX_DOCUMENTATION.md` - Index optimization guide

---

**Last Updated:** December 6, 2025  
**Database:** PostgreSQL (superstore)  
**Total Queries:** 9 SELECT, 4 INSERT  
**Query Types:** JOIN, Aggregate, Window, Date functions
