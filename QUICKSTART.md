# Quick Start Guide

Panduan cepat untuk menjalankan Data Engineering Scraping Project.

## 🚀 Cara Tercepat - Menggunakan Docker

### 1. Persiapan Awal

```bash
# Masuk ke folder project
cd data-engineer-scraping-project

# Pastikan Docker dan Docker Compose terinstall
docker --version
docker-compose --version
```

### 2. Jalankan Semua Service

```bash
# Start semua service (database, scraper, jupyter)
docker-compose up -d

# Lihat status container
docker-compose ps
```

Output yang diharapkan:
```
NAME            IMAGE                           STATUS         PORTS
de_jupyter      data-engineer-scraping-project  Up 10 seconds  0.0.0.0:8888->8888/tcp
de_postgres     postgres:15-alpine              Up 15 seconds  0.0.0.0:5432->5432/tcp
de_scraper      data-engineer-scraping-project  Exited (0)
```

### 3. Lihat Hasil Scraping

```bash
# Lihat log scraper
docker-compose logs scraper

# Lihat log dengan follow
docker-compose logs -f scraper
```

### 4. Akses Jupyter Notebook

```
Buka browser: http://localhost:8888
File: exploration.ipynb
```

### 5. Jalankan Ulang Scraper

```bash
# Untuk scraping ulang
docker-compose restart scraper

# Atau jalankan manual
docker-compose run --rm scraper python app/main.py
```

### 6. Koneksi ke Database

```bash
# Menggunakan psql
docker exec -it de_postgres psql -U postgres -d de_test_danone

# Di dalam psql:
# \dt raw.*          - Lihat tabel di schema raw
# \dt processed.*    - Lihat tabel di schema processed
# SELECT COUNT(*) FROM raw.products;
```

### 7. Matikan Service

```bash
# Stop semua container
docker-compose down

# Stop dan hapus volumes (hapus data)
docker-compose down -v
```

## 💻 Cara Alternatif - Local Development

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt
```

### 2. Setup Database

```bash
# Buat database (pastikan PostgreSQL sudah running)
createdb de_test_danone

# Jalankan script inisialisasi
psql -d de_test_danone -f scripts/init_db.sql
```

### 3. Konfigurasi Environment

```bash
# Copy template env
cp .env.example .env

# Edit .env sesuai kebutuhan
# Pastikan DB_HOST=localhost untuk local development
```

### 4. Jalankan Scraper

```bash
python app/main.py
```

### 5. Akses Jupyter

```bash
jupyter notebook
# Buka exploration.ipynb
```

## 📊 Verifikasi Hasil

### Cek Database via SQL

```sql
-- Total products scraped
SELECT COUNT(*) FROM raw.products;

-- Products by page
SELECT page_number, COUNT(*) as count 
FROM raw.products 
GROUP BY page_number 
ORDER BY page_number;

-- Scraping sessions
SELECT * FROM raw.scraping_logs 
ORDER BY started_at DESC 
LIMIT 5;

-- Latest products (view)
SELECT * FROM processed.latest_products 
LIMIT 10;

-- Statistics by category
SELECT * FROM processed.product_statistics;
```

### Cek via Python

```python
from app.database import DatabaseConnection, get_db_session
from app.database.models import Product, ScrapingLog

# Test connection
DatabaseConnection.test_connection()

# Query products
with get_db_session() as session:
    count = session.query(Product).count()
    print(f"Total products: {count}")
    
    # Get latest 5 products
    products = session.query(Product).order_by(Product.scraped_at.desc()).limit(5).all()
    for p in products:
        print(f"{p.product_name} - ${p.price}")
```

## 🔧 Troubleshooting

### Problem: Database connection failed

**Solution:**
```bash
# Cek PostgreSQL running
docker-compose ps

# Restart database
docker-compose restart db

# Cek logs
docker-compose logs db
```

### Problem: Port 5432 already in use

**Solution 1 - Stop local PostgreSQL:**
```bash
sudo service postgresql stop
```

**Solution 2 - Ubah port di docker-compose.yml:**
```yaml
services:
  db:
    ports:
      - "5433:5432"  # Ubah port external
```

Jangan lupa update `.env`:
```
DB_PORT=5433
```

### Problem: Scraper tidak menghasilkan data

**Solution:**
```bash
# Cek logs detail
docker-compose logs scraper

# Jalankan dalam mode interactive
docker-compose run --rm scraper python app/main.py

# Cek koneksi internet
docker-compose run --rm scraper ping -c 3 webscraper.io
```

### Problem: Permission denied di folder logs

**Solution:**
```bash
chmod -R 755 logs/
```

## 📁 File Output

Hasil scraping tersimpan di:
- **Database**: PostgreSQL schema `raw.products`
- **Logs**: `logs/app.log`
- **Export**: `notebooks/products_export.csv` (setelah run notebook)

## ⚙️ Kustomisasi

### Ubah Target Scraping

Edit `.env`:
```env
# Scrape lebih banyak halaman
MAX_PAGES=50

# Ubah kategori
TARGET_CATEGORY=computers/tablets

# Kurangi delay untuk lebih cepat (hati-hati dengan rate limit!)
REQUEST_DELAY=0.5
```

### Ubah Log Level

Edit `.env`:
```env
# Untuk debug detail
LOG_LEVEL=DEBUG

# Untuk production (hanya info penting)
LOG_LEVEL=WARNING
```

## 🎯 Next Steps

1. ✅ Jalankan scraper dengan Docker
2. ✅ Verifikasi data di database
3. ✅ Eksplorasi data di Jupyter notebook
4. ✅ Analisa hasil scraping
5. 📊 Buat visualisasi tambahan
6. 🔄 Schedule otomatis (gunakan cron atau Airflow)

## 📞 Support

Jika ada masalah:
1. Cek logs: `docker-compose logs scraper`
2. Cek database: `docker exec -it de_postgres psql -U postgres`
3. Review README.md untuk dokumentasi lengkap
4. Cek file konfigurasi di `.env`

---

**Happy Scraping! 🚀**