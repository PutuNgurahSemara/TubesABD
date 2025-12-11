# add_sellers.py
import psycopg2
import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)

DB_CONFIG = dict(
    dbname="superstore",
    user="postgres",
    password="2436",
    host="localhost",
    port="5432"
)

REGIONS = ['East', 'West', 'Central', 'South']

def connect():
    return psycopg2.connect(**DB_CONFIG)

def generate_sellers():
    seller_names = [
        'Tech Solutions Inc', 'Office World', 'Furniture Plus',
        'Digital Mart', 'Supply Chain Co', 'MegaStore LLC',
        'Prime Sellers', 'Quality Goods', 'Best Products',
        'Elite Traders', 'Global Supplies', 'Smart Commerce',
        'Express Sellers', 'Top Vendors', 'Premier Deals',
        'Reliable Stores', 'Fast Shipping Co', 'Value Mart',
        'Super Sellers', 'Trusted Goods'
    ]
    sellers = []
    for i, name in enumerate(seller_names, 1):
        seller_id = f"SELL-{i:04d}"
        region = random.choice(REGIONS)
        rating = round(random.uniform(3.5, 5.0), 2)
        join_date = (datetime.now() - timedelta(days=random.randint(365, 1825))).date()
        sellers.append({
            'seller_id': seller_id,
            'seller_name': name,
            'seller_email': f"{name.lower().replace(' ', '.') }@sellers.com",
            'seller_phone': f"+1-555-{random.randint(1000,9999)}",
            'seller_region': region,
            'seller_rating': rating,
            'join_date': join_date
        })
    return pd.DataFrame(sellers)

def create_sellers_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sellers (
            seller_id VARCHAR(50) PRIMARY KEY,
            seller_name VARCHAR(255),
            seller_email VARCHAR(255),
            seller_phone VARCHAR(20),
            seller_region region_enum,
            seller_rating DECIMAL(3,2),
            join_date DATE
        );
    """)
    conn.commit()
    cur.close()

def add_seller_column(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='order_details' AND column_name='seller_id';
    """)
    if cur.fetchone() is None:
        cur.execute("ALTER TABLE order_details ADD COLUMN seller_id VARCHAR(50);")
        conn.commit()
    cur.close()

def insert_sellers(conn, df):
    cur = conn.cursor()
    for _, r in df.iterrows():
        cur.execute("""
            INSERT INTO sellers (seller_id, seller_name, seller_email, seller_phone, seller_region, seller_rating, join_date)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (seller_id) DO NOTHING;
        """, (r['seller_id'], r['seller_name'], r['seller_email'], r['seller_phone'], r['seller_region'], r['seller_rating'], r['join_date']))
    conn.commit()
    cur.close()

def assign_sellers_to_orders(conn):
    cur = conn.cursor()
    # build map region -> sellers
    cur.execute("SELECT seller_id, seller_region FROM sellers;")
    sellers_by_region = {}
    for sid, region in cur.fetchall():
        sellers_by_region.setdefault(region, []).append(sid)

    # select order_details and customer region
    cur.execute("""
        SELECT od.id, c.region
        FROM order_details od
        JOIN orders o ON od.order_id = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id;
    """)
    rows = cur.fetchall()
    updates = []
    for od_id, cust_region in rows:
        available = sellers_by_region.get(cust_region) or [s for sl in sellers_by_region.values() for s in sl]
        if not available:
            continue
        seller_id = random.choice(available)
        updates.append((seller_id, od_id))

    for seller_id, od_id in updates:
        cur.execute("UPDATE order_details SET seller_id = %s WHERE id = %s;", (seller_id, od_id))

    conn.commit()
    cur.close()

def add_foreign_key(conn):
    cur = conn.cursor()
    try:
        cur.execute("""
            ALTER TABLE order_details
            ADD CONSTRAINT fk_order_details_seller FOREIGN KEY (seller_id) REFERENCES sellers(seller_id);
        """)
        conn.commit()
    except psycopg2.Error:
        conn.rollback()
    cur.close()

def create_indexes(conn):
    cur = conn.cursor()
    cur.execute("CREATE INDEX IF NOT EXISTS idx_order_details_seller_id ON order_details(seller_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sellers_region ON sellers(seller_region);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sellers_rating ON sellers(seller_rating DESC);")
    conn.commit()
    cur.close()

if __name__ == "__main__":
    conn = connect()
    create_sellers_table(conn)
    sellers_df = generate_sellers()
    insert_sellers(conn, sellers_df)
    add_seller_column(conn)
    assign_sellers_to_orders(conn)
    add_foreign_key(conn)
    create_indexes(conn)
    print("Selesai. Total sellers:", len(sellers_df))
    print(sellers_df.head(10).to_string(index=False))
    conn.close()
