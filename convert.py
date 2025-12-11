# convert.py
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import datetime

# ---------- CONFIG ----------
DB_CONFIG = dict(
    dbname="superstore",
    user="postgres",
    password="2436",
    host="localhost",
    port="5432"
)

EXCEL_FILE = "Superstore.xls"  # ganti kalau beda
SAMPLE_ROWS = None  # set ke int kalau mau sample, atau None semua

# Mapping enum normalisasi (sesuaikan jika nilai di file beda)
SEGMENT_MAP = {
    'Consumer': 'Consumer',
    'Corporate': 'Corporate',
    'Home Office': 'Home Office'
}
REGION_MAP = {
    'East': 'East',
    'West': 'West',
    'Central': 'Central',
    'South': 'South'
}
SHIP_MODE_MAP = {
    'First Class': 'First Class',
    'Second Class': 'Second Class',
    'Standard Class': 'Standard Class',
    'Same Day': 'Same Day'
}

# ---------- HELPERS ----------
def norm_str(x):
    if pd.isna(x):
        return None
    return str(x).strip()

def map_enum(value, mapping):
    if value is None:
        return None
    s = str(value).strip()
    # try exact match
    if s in mapping:
        return mapping[s]
    # try case-insensitive match
    low = s.lower()
    for k in mapping:
        if k.lower() == low:
            return mapping[k]
    # fallback: None (or you can return a default)
    return None

def parse_date(x):
    if pd.isna(x):
        return None
    try:
        dt = pd.to_datetime(x)
        return dt.date()
    except Exception:
        return None

# ---------- MAIN ----------
def main():
    # load excel
    df = pd.read_excel(EXCEL_FILE)
    if SAMPLE_ROWS:
        df = df.head(SAMPLE_ROWS)

    # normalize column names (handle spaces)
    df.columns = [c.strip() for c in df.columns]

    # expected columns in Superstore.xls
    # "Order ID","Order Date","Ship Date","Ship Mode","Customer ID",
    # "Customer Name","Segment","Country","City","State","Postal Code","Region",
    # "Product ID","Category","Sub-Category","Product Name","Sales","Quantity","Discount","Profit"

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # CLEAN target tables in safe FK order
    cur.execute("TRUNCATE order_details CASCADE;")
    cur.execute("TRUNCATE orders CASCADE;")
    cur.execute("TRUNCATE products CASCADE;")
    cur.execute("TRUNCATE subcategories CASCADE;")
    cur.execute("TRUNCATE categories CASCADE;")
    cur.execute("TRUNCATE customers CASCADE;")
    conn.commit()

    # -------------------------
    # 1) categories
    # -------------------------
    cats = df["Category"].dropna().map(str).str.strip().unique().tolist()
    categories_data = [(c,) for c in cats]

    cur.execute("CREATE TEMP TABLE tmp_categories (category_name text);")
    execute_values(cur,
        "INSERT INTO tmp_categories (category_name) VALUES %s",
        categories_data
    )
    cur.execute("""
        INSERT INTO categories (category_name)
        SELECT DISTINCT category_name FROM tmp_categories
        ON CONFLICT (category_name) DO NOTHING;
    """)
    cur.execute("DROP TABLE tmp_categories;")
    conn.commit()

    # build map category_name -> category_id
    cur.execute("SELECT category_id, category_name FROM categories;")
    cat_rows = cur.fetchall()
    cat_map = {name: cid for cid, name in cat_rows}

    # -------------------------
    # 2) subcategories
    # -------------------------
    sub_df = df[["Category", "Sub-Category"]].dropna()
    sub_pairs = sub_df.drop_duplicates().apply(lambda r: (r["Category"].strip(), r["Sub-Category"].strip()), axis=1).tolist()

    # Insert subcategories with mapped category_id
    sub_inserts = []
    for cat_name, sub_name in sub_pairs:
        cat_id = cat_map.get(cat_name)
        if cat_id is None:
            continue
        sub_inserts.append((cat_id, sub_name))
    if sub_inserts:
        execute_values(cur,
            "INSERT INTO subcategories (category_id, subcategory_name) VALUES %s ON CONFLICT DO NOTHING;",
            sub_inserts
        )
        conn.commit()

    # build map subcategory_name+category_id -> subcategory_id
    cur.execute("SELECT subcategory_id, category_id, subcategory_name FROM subcategories;")
    sub_rows = cur.fetchall()
    # map by (category_name, sub_name) -> id
    sub_map = {}
    for sid, cid, sname in sub_rows:
        cname = None
        # find cname from cat_map reverse
        for k, v in cat_map.items():
            if v == cid:
                cname = k
                break
        sub_map[(cname, sname)] = sid

    # -------------------------
    # 3) customers
    # -------------------------
    cust_cols = ["Customer ID", "Customer Name", "Segment", "Country", "City", "State", "Postal Code", "Region"]
    customers = df[cust_cols].drop_duplicates(subset=["Customer ID"])

    cust_values = []
    for _, r in customers.iterrows():
        cid = norm_str(r["Customer ID"])
        cname = norm_str(r["Customer Name"])
        segment = map_enum(r.get("Segment"), SEGMENT_MAP)
        country = norm_str(r.get("Country"))
        city = norm_str(r.get("City"))
        state = norm_str(r.get("State"))
        postal = norm_str(r.get("Postal Code"))
        region = map_enum(r.get("Region"), REGION_MAP)
        cust_values.append((cid, cname, segment, country, city, state, postal, region))

    execute_values(cur,
        """
        INSERT INTO customers (customer_id, customer_name, segment, country, city, state, postal_code, region)
        VALUES %s
        ON CONFLICT (customer_id) DO NOTHING;
        """,
        cust_values
    )
    conn.commit()

    # -------------------------
    # 4) products (needs category_id + subcategory_id)
    # -------------------------
    prod_cols = ["Product ID", "Category", "Sub-Category", "Product Name"]
    products = df[prod_cols].drop_duplicates(subset=["Product ID"])

    prod_inserts = []
    for _, r in products.iterrows():
        pid = norm_str(r["Product ID"])
        cat_name = norm_str(r["Category"])
        sub_name = norm_str(r["Sub-Category"])
        pname = norm_str(r["Product Name"])
        cat_id = cat_map.get(cat_name)
        sub_id = sub_map.get((cat_name, sub_name))
        # If sub_id missing, try to find by sub_name alone
        if sub_id is None:
            for (cname, sname), sid in sub_map.items():
                if sname == sub_name:
                    sub_id = sid
                    break
        # fallback: create subcategory if missing
        if cat_id is None:
            continue
        if sub_id is None:
            # insert new subcategory and get id
            cur.execute("INSERT INTO subcategories (category_id, subcategory_name) VALUES (%s,%s) RETURNING subcategory_id;",
                        (cat_id, sub_name))
            sub_id = cur.fetchone()[0]
            conn.commit()
            # update map
            sub_map[(cat_name, sub_name)] = sub_id

        prod_inserts.append((pid, cat_id, sub_id, pname))

    if prod_inserts:
        execute_values(cur,
            """
            INSERT INTO products (product_id, category_id, subcategory_id, product_name)
            VALUES %s
            ON CONFLICT (product_id) DO NOTHING;
            """,
            prod_inserts
        )
        conn.commit()

    # -------------------------
    # 5) orders
    # -------------------------
    order_cols = ["Order ID", "Order Date", "Ship Date", "Ship Mode", "Customer ID"]
    orders = df[order_cols].drop_duplicates(subset=["Order ID"])

    order_values = []
    for _, r in orders.iterrows():
        oid = norm_str(r["Order ID"])
        odate = parse_date(r.get("Order Date"))
        sdate = parse_date(r.get("Ship Date"))
        ship_mode = map_enum(r.get("Ship Mode"), SHIP_MODE_MAP)
        customer_id = norm_str(r.get("Customer ID"))
        order_values.append((oid, odate, sdate, ship_mode, customer_id))

    execute_values(cur,
        """
        INSERT INTO orders (order_id, order_date, ship_date, ship_mode, customer_id)
        VALUES %s
        ON CONFLICT (order_id) DO NOTHING;
        """,
        order_values
    )
    conn.commit()

    # -------------------------
    # 6) order_details
    # -------------------------
    od_cols = ["Order ID", "Product ID", "Sales", "Quantity", "Discount", "Profit"]
    odf = df[od_cols]

    od_inserts = []
    for _, r in odf.iterrows():
        oid = norm_str(r["Order ID"])
        pid = norm_str(r["Product ID"])
        sales = r.get("Sales") if not pd.isna(r.get("Sales")) else 0
        qty = int(r.get("Quantity")) if not pd.isna(r.get("Quantity")) else 0
        discount = r.get("Discount") if not pd.isna(r.get("Discount")) else 0
        profit = r.get("Profit") if not pd.isna(r.get("Profit")) else 0
        od_inserts.append((oid, pid, sales, qty, discount, profit))

    execute_values(cur,
        """
        INSERT INTO order_details (order_id, product_id, sales, quantity, discount, profit)
        VALUES %s;
        """,
        od_inserts
    )
    conn.commit()

    cur.close()
    conn.close()
    print("Import selesai.")
    
if __name__ == "__main__":
    main()
