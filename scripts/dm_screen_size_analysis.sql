-- Pastikan tabel sebelumnya sudah sukses agar kolom screen_size terbaca
DROP TABLE IF EXISTS transformed.dm_screen_price_analysis;

CREATE TABLE transformed.dm_screen_price_analysis AS
SELECT 
    screen_size,
    COUNT(*) as total_products,
    ROUND(AVG(CAST(price AS NUMERIC)), 2) as avg_price,
    MIN(price) as min_price,
    MAX(price) as max_price
FROM transformed.dm_product_specs
WHERE screen_size IS NOT NULL
GROUP BY screen_size
ORDER BY CAST(screen_size AS NUMERIC) ASC;
