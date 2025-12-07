import psycopg2
import pandas as pd


conn = psycopg2.connect(
    dbname="superstore",
    user="postgres",
    password="putu2520",
    host="localhost",
    port="5432"
    )

# ============================================
# CREATE INDEXES FOR PERFORMANCE
# ============================================
def create_indexes():
    """Membuat indexes untuk optimasi query performance"""
    cur = conn.cursor()
    
    print("🔧 Membuat indexes...")
    
    # Index untuk Foreign Keys (mempercepat JOIN)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_order_details_order_id ON order_details(order_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_order_details_product_id ON order_details(product_id);")
    
    # Index untuk kolom yang sering di-filter
    cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_customers_segment ON customers(segment);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_customers_region ON customers(region);")
    
    # Composite Index
    cur.execute("CREATE INDEX IF NOT EXISTS idx_order_details_order_product ON order_details(order_id, product_id);")
    
    # Index untuk sorting
    cur.execute("CREATE INDEX IF NOT EXISTS idx_order_details_sales ON order_details(sales DESC);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_order_details_profit ON order_details(profit DESC);")
    
    conn.commit()
    print("✅ Indexes berhasil dibuat!")
    cur.close()

# ============================================
# OPTIMIZED QUERIES WITH JOIN
# ============================================
    
def load_data():
    """Load semua data dengan JOIN 5 tabel termasuk sellers (sudah teroptimasi dengan index)"""
    query = """
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
    """
    
    # Load data
    data = pd.read_sql(query, conn)
    
    # Convert numeric columns
    numeric_cols = ['quantity', 'sales', 'profit', 'discount', 'seller_rating']
    for col in numeric_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
    
    return data

def get_sales_by_category():
    """Query optimized: Sales per kategori (menggunakan index pada category)"""
    query = """
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
    """
    return pd.read_sql(query, conn)

def get_sales_by_segment():
    """Query optimized: Sales per segment (menggunakan index pada segment)"""
    query = """
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
    """
    return pd.read_sql(query, conn)

def get_top_products(limit=10):
    """Query optimized: Top produk terlaris"""
    query = f"""
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
    LIMIT {limit};
    """
    return pd.read_sql(query, conn)

def get_top_customers(limit=10):
    """Query optimized: Top customer berdasarkan total pembelian"""
    query = f"""
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
    LIMIT {limit};
    """
    return pd.read_sql(query, conn)

def get_sales_trend_monthly():
    """Query optimized: Trend penjualan per bulan"""
    query = """
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
    """
    return pd.read_sql(query, conn)

def get_top_sellers(limit=10):
    """Query: Top sellers berdasarkan total sales"""
    query = f"""
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
    LIMIT {limit};
    """
    return pd.read_sql(query, conn)

def get_seller_performance():
    """Query: Performa seller berdasarkan rating vs profit"""
    query = """
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
    """
    return pd.read_sql(query, conn)

def get_profit_by_category():
    """Query optimized: Profit per kategori untuk stacked bar chart"""
    query = """
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
    """
    return pd.read_sql(query, conn)

def add_data():
    cur = conn.cursor()

    df = pd.read_excel('Superstore.xls').head(500)

    # 1. INSERT customers
    customers = df[[
        "Customer ID", "Customer Name", "Segment",
        "Country", "City", "State", "Postal Code", "Region"
    ]].drop_duplicates()

    for _, row in customers.iterrows():
        cur.execute("""
            INSERT INTO customers (customer_id, customer_name, segment, country, city, state, postal_code, region)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (customer_id) DO NOTHING;
        """, tuple(row))

    # 2. INSERT products
    products = df[[
        "Product ID","Category","Sub-Category","Product Name"
    ]].drop_duplicates()

    for _, row in products.iterrows():
        cur.execute("""
            INSERT INTO products (product_id, category, sub_category, product_name)
            VALUES (%s,%s,%s,%s)
            ON CONFLICT (product_id) DO NOTHING;
        """, tuple(row))

    # 3. INSERT orders
    orders = df[[
        "Order ID","Order Date","Ship Date","Ship Mode","Customer ID"
    ]].drop_duplicates()

    for _, row in orders.iterrows():
        cur.execute("""
            INSERT INTO orders (order_id, order_date, ship_date, ship_mode, customer_id)
            VALUES (%s,%s,%s,%s,%s)
            ON CONFLICT (order_id) DO NOTHING;
        """, tuple(row))

    # 4. INSERT order_details
    for _, row in df.iterrows():
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

    conn.commit()
    print("✅ Import selesai.")
    
    # Otomatis buat indexes setelah import
    print("\n🔧 Membuat indexes untuk optimasi...")
    create_indexes()

if __name__ == "__main__":
    add_data()

