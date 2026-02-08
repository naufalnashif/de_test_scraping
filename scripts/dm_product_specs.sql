DROP TABLE IF EXISTS transformed.dm_product_specs;

CREATE TABLE transformed.dm_product_specs AS
WITH extracted AS (
    SELECT 
        *, -- Mengambil semua kolom original dari tabel raw
        split_part(product_name, ' ', 1) as brand,
        
        -- SCREEN SIZE: Ekstrak dulu, lalu hapus semua karakter selain angka dan titik (.)
        -- Ini akan mengubah '17.3"' menjadi '17.3'
        regexp_replace(
            substring(description from '[1][0-9]\.?[0-9]?\s*(?:"|inch|Inch)'), 
            '[^0-9.]', '', 'g'
        ) as screen_size,
        -- DISPLAY TYPE: Mencari keyword layar
        substring(description from '(?i)IPS|OLED|LED|TN|FHD|Full HD|HD|Touch') as display_type,
        -- OS: Mencari sistem operasi
        substring(description from '(?i)Windows|Win 10|Win 11|Linux|Ubuntu|DOS|FreeDOS|Mac OS') as os,
        -- STORAGE: Mencari kapasitas (GB/TB)
        substring(description from '[0-9]+\s*[GT]B\s*[SHD]*[SDH]*') as ram,
        substring(description from '[0-9]+\s*[GT]B(?=\s*(SSD|HDD|SSHD|Hybrid|\+))') as storage,
        substring(description from '(?i)SSD|HDD|Hybrid') AS storage_type,
        -- PROCESSOR
        substring(description from '(?i)Intel [^,]+|AMD [^,]+|Core [^,]+|Ryzen [^,]+|Celeron [^,]+|Pentium [^,]+') as processor,
        -- GRAPHICS
        substring(description from '(?i)Nvidia|Geforce|Radeon|Intel HD|Intel UHD|RTX [0-9]+|GTX [0-9]+') as graphics_card
    FROM raw.products
)
SELECT * FROM extracted;