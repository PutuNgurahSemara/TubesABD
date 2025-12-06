-- ============================================
-- OPTIMASI INDEX: Hapus index yang duplicate/tidak perlu
-- ============================================

-- 1. Hapus index duplicate
DROP INDEX IF EXISTS idx_order_details_order;  -- duplicate dengan idx_order_details_order_id
DROP INDEX IF EXISTS idx_order_details_product;  -- duplicate dengan idx_order_details_product_id
DROP INDEX IF EXISTS idx_orders_customer;  -- duplicate dengan idx_orders_customer_id

-- 2. Hapus index yang tidak terlalu berguna untuk dataset kecil (500 rows)
DROP INDEX IF EXISTS idx_order_details_sales;  -- ORDER BY sales jarang digunakan
DROP INDEX IF EXISTS idx_order_details_profit;  -- ORDER BY profit jarang digunakan
DROP INDEX IF EXISTS idx_customers_segment;  -- Filter segment tidak sering
DROP INDEX IF EXISTS idx_sellers_rating;  -- Sort by rating tidak kritis

-- 3. Hapus composite index yang redundant
DROP INDEX IF EXISTS idx_order_details_order_product;  -- Sudah ada index terpisah

-- ============================================
-- INDEX YANG TETAP DIPERTAHANKAN (ESSENTIAL)
-- ============================================
-- ✅ Primary Keys (otomatis):
--    - customers_pkey
--    - products_pkey
--    - orders_pkey
--    - order_details_pkey
--    - sellers_pkey

-- ✅ Foreign Keys (untuk JOIN):
--    - idx_order_details_order_id (order_details.order_id)
--    - idx_order_details_product_id (order_details.product_id)
--    - idx_order_details_seller_id (order_details.seller_id)
--    - idx_orders_customer_id (orders.customer_id)

-- ✅ Filter yang sering digunakan:
--    - idx_orders_order_date (untuk filter tanggal)
--    - idx_products_category (untuk groupby category)
--    - idx_customers_region (untuk filter region)
--    - idx_sellers_region (untuk filter seller region)

-- Total: 13 indexes (turun dari 21)

-- Verifikasi hasil
SELECT 
    schemaname,
    relname as table_name,
    indexrelname as index_name,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes 
WHERE schemaname = 'public'
ORDER BY relname, indexrelname;
