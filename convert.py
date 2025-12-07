import pandas as pd
import psycopg2

conn = psycopg2.connect(
    dbname="superstore",
    user="postgres",
    password="2436",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

df = pd.read_excel('Superstore.xls').head(500)

cur.execute("DELETE FROM order_details")
cur.execute("DELETE FROM orders")
cur.execute("DELETE FROM products")
cur.execute("DElETE FROM customers")
conn.commit()

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
print("Import selesai.")
