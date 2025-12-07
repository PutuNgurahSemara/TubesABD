import psycopg2
import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)

conn = psycopg2.connect(
    dbname="superstore",
    user="postgres",
    password="putu2520",
    host="localhost",
    port="5432"
)

def generate_sellers():
    """Generate data sellers yang realistis"""

    random.seed(42)
    
    # Data sample untuk generate sellers
    regions = ['East', 'West', 'Central', 'South']
    seller_names = [
        'Tech Solutions Inc', 'Office World', 'Furniture Plus',
        'Digital Mart', 'Supply Chain Co', 'MegaStore LLC',
        'Prime Sellers', 'Quality Goods', 'Best Products',
        'Elite Traders', 'Global Supplies', 'Smart Commerce',
        'Express Sellers', 'Top Vendors', 'Premier Deals',
        'Reliable Stores', 'Fast Shipping Co', 'Value Mart',
        'Super Sellers', 'Trusted Goods'
    ]
    
    sellers_data = []
    for i, name in enumerate(seller_names, 1):
        seller_id = f"SELL-{i:04d}"
        region = random.choice(regions)
        rating = round(random.uniform(3.5, 5.0), 2)
        join_date = datetime.now() - timedelta(days=random.randint(365, 1825))  # 1-5 tahun lalu
        
        sellers_data.append({
            'seller_id': seller_id,
            'seller_name': name,
            'seller_email': f"{name.lower().replace(' ', '.')}@sellers.com",
            'seller_phone': f"+1-555-{random.randint(1000, 9999)}",
            'seller_region': region,
            'seller_rating': rating,
            'join_date': join_date.date()
        })
    
    return pd.DataFrame(sellers_data)

def add_seller_column():
    """Tambahkan kolom seller_id ke tabel order_details"""
    cur = conn.cursor()
    
    print("🔧 Menambahkan kolom seller_id ke order_details...")
    
    # Cek apakah kolom sudah ada
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='order_details' AND column_name='seller_id';
    """)
    
    if cur.fetchone() is None:
        # Tambah kolom baru
        cur.execute("ALTER TABLE order_details ADD COLUMN seller_id VARCHAR(50);")
        print("✅ Kolom seller_id berhasil ditambahkan")
    else:
        print("ℹ️ Kolom seller_id sudah ada")
    
    conn.commit()
    cur.close()

def create_sellers_table():
    """Buat tabel sellers jika belum ada"""
    cur = conn.cursor()
    
    print("🔧 Membuat tabel sellers...")
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sellers (
            seller_id VARCHAR(50) PRIMARY KEY,
            seller_name VARCHAR(255),
            seller_email VARCHAR(255),
            seller_phone VARCHAR(50),
            seller_region VARCHAR(50),
            seller_rating DECIMAL(3,2),
            join_date DATE
        );
    """)
    
    conn.commit()
    print("✅ Tabel sellers berhasil dibuat")
    cur.close()

def insert_sellers(df):
    """Insert data sellers ke database"""
    cur = conn.cursor()
    
    print("📥 Memasukkan data sellers...")
    
    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO sellers (seller_id, seller_name, seller_email, seller_phone, seller_region, seller_rating, join_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (seller_id) DO NOTHING;
        """, tuple(row))
    
    conn.commit()
    print(f"✅ {len(df)} sellers berhasil ditambahkan")
    cur.close()

def assign_sellers_to_orders():
    """Assign seller_id secara random ke setiap order_details berdasarkan region"""
    random.seed(42)
    cur = conn.cursor()
    
    print("🔧 Mengassign sellers ke order_details...")
    
    # Ambil semua seller_id per region
    cur.execute("SELECT seller_id, seller_region FROM sellers;")
    sellers_by_region = {}
    for seller_id, region in cur.fetchall():
        if region not in sellers_by_region:
            sellers_by_region[region] = []
        sellers_by_region[region].append(seller_id)
    
    # Update order_details dengan seller_id yang sesuai dengan region customer
    cur.execute("""
        SELECT od.id, c.region 
        FROM order_details od
        JOIN orders o ON od.order_id = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id;
    """)
    
    updates = []
    for order_detail_id, customer_region in cur.fetchall():
        # Pilih seller dari region yang sama atau random jika tidak ada
        available_sellers = sellers_by_region.get(customer_region, [])
        if not available_sellers:
            # Fallback ke seller random dari region mana saja
            available_sellers = [s for sellers in sellers_by_region.values() for s in sellers]
        
        seller_id = random.choice(available_sellers)
        updates.append((seller_id, order_detail_id))
    
    # Batch update
    for seller_id, order_detail_id in updates:
        cur.execute("UPDATE order_details SET seller_id = %s WHERE id = %s;", (seller_id, order_detail_id))
    
    conn.commit()
    print(f"✅ {len(updates)} order_details berhasil di-assign ke sellers")
    cur.close()

def add_foreign_key_constraint():
    """Tambahkan foreign key constraint untuk seller_id"""
    cur = conn.cursor()
    
    print("🔧 Menambahkan foreign key constraint...")
    
    try:
        cur.execute("""
            ALTER TABLE order_details 
            ADD CONSTRAINT fk_order_details_seller 
            FOREIGN KEY (seller_id) REFERENCES sellers(seller_id);
        """)
        conn.commit()
        print("✅ Foreign key constraint berhasil ditambahkan")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"ℹ️ Foreign key constraint sudah ada atau error: {e}")
    
    cur.close()

def create_indexes():
    """Buat indexes untuk optimasi"""
    cur = conn.cursor()
    
    print("🔧 Membuat indexes...")
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_order_details_seller_id ON order_details(seller_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sellers_region ON sellers(seller_region);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sellers_rating ON sellers(seller_rating DESC);")
    
    conn.commit()
    print("✅ Indexes berhasil dibuat")
    cur.close()

if __name__ == "__main__":
    print("\n🚀 Memulai proses penambahan tabel sellers...\n")
    
    # 1. Buat tabel sellers
    create_sellers_table()
    
    # 2. Generate dan insert data sellers
    sellers_df = generate_sellers()
    insert_sellers(sellers_df)
    
    # 3. Tambah kolom seller_id ke order_details
    add_seller_column()
    
    # 4. Assign sellers ke order_details
    assign_sellers_to_orders()
    
    # 5. Tambah foreign key constraint
    add_foreign_key_constraint()
    
    # 6. Buat indexes
    create_indexes()
    
    print("\n✅ Proses selesai!")
    print(f"\n📊 Total sellers: {len(sellers_df)}")
    
    # Tampilkan sample data
    print("\n📋 Sample sellers:")
    print(sellers_df.head(10).to_string(index=False))
    
    conn.close()
