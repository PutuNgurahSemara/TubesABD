import psycopg2
import pandas as pd

# Koneksi ke database
conn = psycopg2.connect(
    dbname="superstore",
    user="postgres",
    password="putu2520",
    host="localhost",
    port="5432"
)

print("🔄 Mengekspor data dari PostgreSQL ke CSV...")

# Query untuk mengambil semua data
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

# Baca data dan simpan ke CSV
df = pd.read_sql(query, conn)
df.to_csv('superstore_data.csv', index=False)

print(f"✅ Berhasil mengekspor {len(df)} baris data ke 'superstore_data.csv'")
print(f"📊 Kolom yang diekspor: {', '.join(df.columns)}")

conn.close()
