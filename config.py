import psycopg2
import pandas as pd


conn = psycopg2.connect(
    dbname="superstore",
    user="postgres",
    password="2436",
    host="localhost",
    port="5432"
)



def load_data():
    """Load semua data dengan JOIN 7 tabel (termasuk categories & subcategories)"""
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
        cat.category_name as category,
        sub.subcategory_name as sub_category,
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
    INNER JOIN categories cat ON p.category_id = cat.category_id
    INNER JOIN subcategories sub ON p.subcategory_id = sub.subcategory_id
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

def get_categories():
    query = """
    SELECT 
        category_id,
        category_name,
        description
    FROM categories
    ORDER BY category_id;
    """
    return pd.read_sql(query, conn)


def get_subcategories():
    query = """
    SELECT
        subcategory_id,
        category_id,
        subcategory_name
    FROM subcategories
    ORDER BY subcategory_id;
    """
    return pd.read_sql(query, conn)


def get_sellers():
    query = """
    SELECT
        seller_id,
        seller_name,
        seller_email,
        seller_phone,
        seller_region,
        seller_rating,
        join_date
    FROM sellers
    ORDER BY seller_id;
    """
    return pd.read_sql(query, conn)


def get_customers():
    query = """
    SELECT
        customer_id,
        customer_name,
        segment,
        country,
        city,
        state,
        postal_code,
        region
    FROM customers
    ORDER BY customer_id;
    """
    return pd.read_sql(query, conn)


def get_products():
    query = """
    SELECT
        product_id,
        category_id,
        subcategory_id,
        product_name
    FROM products
    ORDER BY product_id;
    """
    return pd.read_sql(query, conn)


def get_orders():
    query = """
    SELECT
        order_id,
        order_date,
        ship_date,
        ship_mode,
        customer_id
    FROM orders
    ORDER BY order_date DESC;
    """
    return pd.read_sql(query, conn)


def get_order_details():
    query = """
    SELECT
        id,
        order_id,
        product_id,
        seller_id,
        sales,
        quantity,
        discount,
        profit
    FROM order_details
    ORDER BY id;
    """
    return pd.read_sql(query, conn)


def get_sales_by_category():
    """Query optimized: Sales per kategori"""
    query = """
    SELECT 
        cat.category_name as category,
        COUNT(d.id) as total_orders,
        SUM(d.quantity) as total_quantity,
        SUM(d.sales) as total_sales,
        SUM(d.profit) as total_profit,
        AVG(d.sales) as avg_sales
    FROM order_details d
    INNER JOIN products p ON d.product_id = p.product_id
    INNER JOIN categories cat ON p.category_id = cat.category_id
    GROUP BY cat.category_name
    ORDER BY total_sales DESC;
    """
    return pd.read_sql(query, conn)

def get_sales_by_segment():
    """Query optimized: Sales per segment"""
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
        cat.category_name as category,
        sub.subcategory_name as sub_category,
        COUNT(d.id) as order_count,
        SUM(d.quantity) as total_quantity,
        SUM(d.sales) as total_sales,
        SUM(d.profit) as total_profit
    FROM order_details d
    INNER JOIN products p ON d.product_id = p.product_id
    INNER JOIN categories cat ON p.category_id = cat.category_id
    INNER JOIN subcategories sub ON p.subcategory_id = sub.subcategory_id
    GROUP BY p.product_id, p.product_name, cat.category_name, sub.subcategory_name
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
        cat.category_name as category,
        SUM(d.profit) as total_profit,
        SUM(CASE WHEN d.profit > 0 THEN d.profit ELSE 0 END) as positive_profit,
        SUM(CASE WHEN d.profit < 0 THEN d.profit ELSE 0 END) as negative_profit,
        COUNT(d.id) as order_count
    FROM order_details d
    INNER JOIN products p ON d.product_id = p.product_id
    INNER JOIN categories cat ON p.category_id = cat.category_id
    GROUP BY cat.category_name
    ORDER BY total_profit DESC;
    """
    return pd.read_sql(query, conn)

def get_order_invoice(order_id):
    """Get complete invoice detail for specific order"""
    query = f"""
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
        p.product_name,
        cat.category_name,
        sub.subcategory_name,
        s.seller_name,
        s.seller_region,
        d.quantity,
        d.sales,
        d.discount,
        d.profit
    FROM order_details d
    INNER JOIN orders o ON d.order_id = o.order_id
    INNER JOIN customers c ON o.customer_id = c.customer_id
    INNER JOIN products p ON d.product_id = p.product_id
    INNER JOIN categories cat ON p.category_id = cat.category_id
    INNER JOIN subcategories sub ON p.subcategory_id = sub.subcategory_id
    INNER JOIN sellers s ON d.seller_id = s.seller_id
    WHERE o.order_id = '{order_id}'
    ORDER BY d.id;
    """
    return pd.read_sql(query, conn)


def search_orders(search_term="", limit=50):
    """Search orders by order_id, customer name, or product name"""
    query = f"""
    SELECT DISTINCT
        o.order_id,
        o.order_date,
        c.customer_name,
        c.city,
        c.state,
        COUNT(d.id) as total_items,
        SUM(d.sales) as total_sales,
        SUM(d.profit) as total_profit
    FROM orders o
    INNER JOIN customers c ON o.customer_id = c.customer_id
    INNER JOIN order_details d ON o.order_id = d.order_id
    WHERE 
        o.order_id ILIKE '%{search_term}%' OR
        c.customer_name ILIKE '%{search_term}%'
    GROUP BY o.order_id, o.order_date, c.customer_name, c.city, c.state
    ORDER BY o.order_date DESC
    LIMIT {limit};
    """
    return pd.read_sql(query, conn)

def get_rfm_analysis():
    """Get RFM (Recency, Frequency, Monetary) Analysis"""
    query = """
    WITH customer_metrics AS (
        SELECT 
            c.customer_id,
            c.customer_name,
            c.segment,
            c.region,
            MAX(o.order_date) as last_order_date,
            COUNT(DISTINCT o.order_id) as frequency,
            SUM(d.sales) as monetary
        FROM customers c
        INNER JOIN orders o ON c.customer_id = o.customer_id
        INNER JOIN order_details d ON o.order_id = d.order_id
        GROUP BY c.customer_id, c.customer_name, c.segment, c.region
    ),
    rfm_calc AS (
        SELECT 
            *,
            CURRENT_DATE - last_order_date as recency_days,
            NTILE(5) OVER (ORDER BY CURRENT_DATE - last_order_date DESC) as r_score,
            NTILE(5) OVER (ORDER BY frequency ASC) as f_score,
            NTILE(5) OVER (ORDER BY monetary ASC) as m_score
        FROM customer_metrics
    )
    SELECT 
        customer_id,
        customer_name,
        segment,
        region,
        last_order_date,
        recency_days,
        frequency,
        monetary,
        r_score,
        f_score,
        m_score,
        (r_score + f_score + m_score) as rfm_score,
        CASE 
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost Customers'
            WHEN r_score >= 3 AND f_score <= 2 AND m_score >= 3 THEN 'Potential Loyalists'
            WHEN m_score >= 4 THEN 'Big Spenders'
            ELSE 'Regular Customers'
        END as customer_segment
    FROM rfm_calc
    ORDER BY rfm_score DESC, monetary DESC;
    """
    return pd.read_sql(query, conn)


def get_rfm_segment_summary():
    """Get summary statistics per RFM segment"""
    query = """
    WITH customer_metrics AS (
        SELECT 
            c.customer_id,
            c.customer_name,
            c.segment,
            c.region,
            MAX(o.order_date) as last_order_date,
            COUNT(DISTINCT o.order_id) as frequency,
            SUM(d.sales) as monetary
        FROM customers c
        INNER JOIN orders o ON c.customer_id = o.customer_id
        INNER JOIN order_details d ON o.order_id = d.order_id
        GROUP BY c.customer_id, c.customer_name, c.segment, c.region
    ),
    rfm_calc AS (
        SELECT 
            *,
            CURRENT_DATE - last_order_date as recency_days,
            NTILE(5) OVER (ORDER BY CURRENT_DATE - last_order_date DESC) as r_score,
            NTILE(5) OVER (ORDER BY frequency ASC) as f_score,
            NTILE(5) OVER (ORDER BY monetary ASC) as m_score
        FROM customer_metrics
    ),
    rfm_segments AS (
        SELECT 
            *,
            CASE 
                WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
                WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
                WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
                WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
                WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost Customers'
                WHEN r_score >= 3 AND f_score <= 2 AND m_score >= 3 THEN 'Potential Loyalists'
                WHEN m_score >= 4 THEN 'Big Spenders'
                ELSE 'Regular Customers'
            END as customer_segment
        FROM rfm_calc
    )
    SELECT 
        customer_segment,
        COUNT(*) as customer_count,
        ROUND(AVG(recency_days), 0) as avg_recency_days,
        ROUND(AVG(frequency), 1) as avg_frequency,
        ROUND(AVG(monetary), 2) as avg_monetary,
        ROUND(SUM(monetary), 2) as total_revenue
    FROM rfm_segments
    GROUP BY customer_segment
    ORDER BY total_revenue DESC;
    """
    return pd.read_sql(query, conn)
