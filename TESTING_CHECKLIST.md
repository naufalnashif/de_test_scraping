# Testing Checklist

Checklist untuk memastikan semua komponen berfungsi dengan baik.

## ✅ Pre-requisites Check

- [ ] Docker installed: `docker --version`
- [ ] Docker Compose installed: `docker-compose --version`
- [ ] Port 5432 available (PostgreSQL)
- [ ] Port 8888 available (Jupyter)
- [ ] Internet connection available

## ✅ File Structure Check

```bash
# Verifikasi semua file ada
cd data-engineer-scraping-project

# Cek file utama
ls -la README.md
ls -la QUICKSTART.md
ls -la docker-compose.yml
ls -la Dockerfile
ls -la requirements.txt
ls -la .env

# Cek struktur app/
ls -la app/main.py
ls -la app/config/settings.py
ls -la app/database/connection.py
ls -la app/database/models.py
ls -la app/scraper/base_scraper.py
ls -la app/scraper/example_scraper.py
ls -la app/services/ingest_service.py
ls -la app/utils/logger.py

# Cek notebooks dan scripts
ls -la notebooks/exploration.ipynb
ls -la scripts/init_db.sql
```

**Expected**: Semua file harus ada tanpa error.

## ✅ Docker Deployment Test

### 1. Build Images

```bash
docker-compose build
```

**Expected**: Build sukses tanpa error.

**Checklist**:
- [ ] PostgreSQL image pulled
- [ ] Python dependencies installed
- [ ] Application code copied
- [ ] No build errors

### 2. Start Services

```bash
docker-compose up -d
```

**Expected**: Semua services start sukses.

**Checklist**:
- [ ] Database container running: `de_postgres`
- [ ] Jupyter container running: `de_jupyter`
- [ ] Scraper container exited with code 0

### 3. Check Container Status

```bash
docker-compose ps
```

**Expected Output**:
```
NAME            STATUS
de_postgres     Up (healthy)
de_jupyter      Up
de_scraper      Exited (0)
```

**Checklist**:
- [ ] PostgreSQL: Status "Up" dengan health check passed
- [ ] Jupyter: Status "Up"
- [ ] Scraper: Status "Exited (0)" (sukses)

### 4. Database Connection Test

```bash
# Test koneksi dari host
docker exec -it de_postgres psql -U postgres -d de_test_danone -c "SELECT 1;"

# Expected output: 
#  ?column? 
# ----------
#         1
```

**Checklist**:
- [ ] Koneksi database berhasil
- [ ] Database `de_test_danone` exists

### 5. Schema Verification

```bash
docker exec -it de_postgres psql -U postgres -d de_test_danone
```

Di dalam psql, jalankan:

```sql
-- Check schemas
\dn

-- Expected: raw, processed schemas exist

-- Check tables
\dt raw.*
\dt processed.*

-- Expected:
-- raw.products
-- raw.scraping_logs
-- processed.products_clean

-- Check views
\dv processed.*

-- Expected:
-- processed.latest_products
-- processed.product_statistics
```

**Checklist**:
- [ ] Schema `raw` exists
- [ ] Schema `processed` exists
- [ ] Table `raw.products` exists
- [ ] Table `raw.scraping_logs` exists
- [ ] Table `processed.products_clean` exists
- [ ] View `processed.latest_products` exists
- [ ] View `processed.product_statistics` exists

### 6. Scraping Results Verification

```bash
# Check scraper logs
docker-compose logs scraper | tail -50
```

**Expected dalam logs**:
- ✅ Configuration validated
- ✅ Database connection successful
- ✅ Scraper initialized
- ✅ Starting web scraping
- ✅ Page 1: Scraped X products
- ✅ Page 2: Scraped X products
- ✅ Data ingestion completed
- ✅ Successfully inserted: X
- ✅ PIPELINE COMPLETED SUCCESSFULLY

**Checklist**:
- [ ] Scraping started successfully
- [ ] Multiple pages scraped (at least 5)
- [ ] Products extracted from each page
- [ ] Data ingestion completed
- [ ] No critical errors
- [ ] Pipeline completed successfully

### 7. Database Data Verification

```bash
docker exec -it de_postgres psql -U postgres -d de_test_danone
```

```sql
-- Count products
SELECT COUNT(*) FROM raw.products;
-- Expected: > 0 (should have products)

-- Sample products
SELECT product_name, price, rating 
FROM raw.products 
LIMIT 5;
-- Expected: Laptop products with data

-- Check scraping logs
SELECT scrape_session_id, status, records_scraped, duration_seconds
FROM raw.scraping_logs 
ORDER BY started_at DESC 
LIMIT 5;
-- Expected: At least 1 successful log entry

-- Statistics
SELECT * FROM processed.product_statistics;
-- Expected: Statistics for laptops category
```

**Checklist**:
- [ ] Products table contains data (COUNT > 0)
- [ ] Products have valid data (name, price, rating)
- [ ] Scraping log exists with SUCCESS status
- [ ] Statistics view returns data

### 8. Jupyter Notebook Test

```bash
# Open browser
open http://localhost:8888
```

**Or manually**: `http://localhost:8888`

**In Jupyter**:
1. Open `exploration.ipynb`
2. Run all cells: Cell → Run All

**Checklist**:
- [ ] Jupyter accessible at port 8888
- [ ] Notebook loads without error
- [ ] Database connection successful
- [ ] Data loaded into DataFrame
- [ ] Visualizations render correctly
- [ ] No errors in any cell
- [ ] CSV export created

### 9. Log Files Verification

```bash
# Check log directory
ls -la logs/

# Check log content
tail -50 logs/app.log
```

**Checklist**:
- [ ] Log directory exists
- [ ] `app.log` file exists
- [ ] Log contains scraping activity
- [ ] Timestamps are correct
- [ ] No unexpected errors

## ✅ Functionality Tests

### Test 1: Re-run Scraper

```bash
docker-compose restart scraper
docker-compose logs scraper | tail -30
```

**Expected**: 
- Second run completes successfully
- Duplicates detected and skipped
- New timestamp products added

**Checklist**:
- [ ] Scraper runs successfully again
- [ ] Duplicate handling works
- [ ] New scrape session logged

### Test 2: Database Queries

```sql
-- Test all views
SELECT COUNT(*) FROM processed.latest_products;
SELECT * FROM processed.product_statistics;

-- Test aggregations
SELECT 
    AVG(price) as avg_price,
    MIN(price) as min_price,
    MAX(price) as max_price
FROM raw.products;

-- Test joins (if needed)
SELECT p.product_name, p.price, l.scrape_session_id
FROM raw.products p
JOIN raw.scraping_logs l ON DATE(p.scraped_at) = DATE(l.started_at)
LIMIT 5;
```

**Checklist**:
- [ ] All queries execute without error
- [ ] Results are reasonable
- [ ] No NULL values where unexpected

### Test 3: Data Quality

```sql
-- Check for NULL values
SELECT 
    COUNT(*) FILTER (WHERE product_name IS NULL) as null_names,
    COUNT(*) FILTER (WHERE price IS NULL) as null_prices,
    COUNT(*) FILTER (WHERE rating IS NULL) as null_ratings
FROM raw.products;

-- Check price range
SELECT MIN(price), MAX(price) FROM raw.products;
-- Expected: Reasonable laptop prices ($200-$3000)

-- Check rating range
SELECT DISTINCT rating FROM raw.products ORDER BY rating;
-- Expected: 1, 2, 3, 4, 5 (or subset)
```

**Checklist**:
- [ ] No unexpected NULL values
- [ ] Price values are reasonable
- [ ] Rating values are 1-5
- [ ] All timestamps are valid

## ✅ Performance Tests

### Test 4: Scraping Speed

```bash
# Check duration in logs
docker exec -it de_postgres psql -U postgres -d de_test_danone -c \
"SELECT duration_seconds FROM raw.scraping_logs ORDER BY started_at DESC LIMIT 1;"
```

**Expected**: 
- 1 page ≈ 1-2 seconds (dengan delay 1s)
- 10 pages ≈ 10-20 seconds
- 20 pages ≈ 20-40 seconds

**Checklist**:
- [ ] Duration reasonable for number of pages
- [ ] No timeouts
- [ ] Consistent performance

### Test 5: Database Performance

```sql
-- Test index usage
EXPLAIN ANALYZE 
SELECT * FROM raw.products 
WHERE category = 'computers/laptops';

-- Test view performance
EXPLAIN ANALYZE 
SELECT * FROM processed.latest_products 
LIMIT 100;
```

**Checklist**:
- [ ] Queries use indexes
- [ ] Query execution < 100ms
- [ ] No sequential scans on large tables

## ✅ Error Handling Tests

### Test 6: Network Error Simulation

```bash
# Stop scraper in middle of run (if running)
docker-compose stop scraper

# Check logs for graceful shutdown
docker-compose logs scraper | grep -i "error\|warning"
```

**Checklist**:
- [ ] Errors logged properly
- [ ] No data corruption
- [ ] Database state consistent

### Test 7: Database Disconnect

```bash
# Stop database while scraper running
docker-compose stop db

# Start new scraper
docker-compose run --rm scraper python app/main.py

# Expected: Clear error message about connection
```

**Checklist**:
- [ ] Error message clear
- [ ] No crash/hang
- [ ] Proper error logging

## ✅ Cleanup Tests

### Test 8: Stop and Remove

```bash
# Stop all services
docker-compose down

# Check containers stopped
docker-compose ps
# Expected: No containers running
```

**Checklist**:
- [ ] All containers stopped
- [ ] No errors during shutdown

### Test 9: Data Persistence

```bash
# Restart services
docker-compose up -d

# Check data still exists
docker exec -it de_postgres psql -U postgres -d de_test_danone -c \
"SELECT COUNT(*) FROM raw.products;"

# Expected: Same count as before
```

**Checklist**:
- [ ] Data persisted after restart
- [ ] Database intact
- [ ] Volumes working correctly

### Test 10: Complete Cleanup

```bash
# Remove everything including volumes
docker-compose down -v

# Verify volumes removed
docker volume ls | grep data-engineer

# Expected: No volumes found
```

**Checklist**:
- [ ] Volumes removed
- [ ] Clean slate for fresh start

## 📊 Final Verification Summary

Print this checklist and check each item:

### Core Functionality ✅
- [ ] Docker deployment successful
- [ ] Database initialized correctly
- [ ] Scraper collects data
- [ ] Data ingested into database
- [ ] Logs created properly
- [ ] Jupyter notebook works

### Data Quality ✅
- [ ] Products have all required fields
- [ ] No data corruption
- [ ] Duplicates handled
- [ ] Timestamps correct

### Performance ✅
- [ ] Scraping speed acceptable
- [ ] Database queries fast
- [ ] No memory leaks
- [ ] Resource usage reasonable

### Error Handling ✅
- [ ] Errors logged properly
- [ ] Graceful degradation
- [ ] Clear error messages
- [ ] No silent failures

### Documentation ✅
- [ ] README clear and complete
- [ ] QUICKSTART easy to follow
- [ ] Code well commented
- [ ] Database schema documented

## 🎯 Success Criteria

Project is ready for submission if:

1. ✅ All docker services start successfully
2. ✅ Scraper collects at least 50 products
3. ✅ Data stored in PostgreSQL correctly
4. ✅ Jupyter notebook runs without errors
5. ✅ Logs are readable and informative
6. ✅ No critical errors in any component
7. ✅ Documentation is complete and accurate
8. ✅ Code is clean and well-organized

## 📝 Test Results Template

```
===========================================
TEST EXECUTION REPORT
===========================================
Date: _______________
Tester: _______________

DOCKER TESTS:
  Build:          [ PASS / FAIL ]
  Start:          [ PASS / FAIL ]
  Status:         [ PASS / FAIL ]
  
DATABASE TESTS:
  Connection:     [ PASS / FAIL ]
  Schema:         [ PASS / FAIL ]
  Data:           [ PASS / FAIL ]
  
SCRAPER TESTS:
  Execution:      [ PASS / FAIL ]
  Data Quality:   [ PASS / FAIL ]
  Logging:        [ PASS / FAIL ]
  
JUPYTER TESTS:
  Access:         [ PASS / FAIL ]
  Notebook:       [ PASS / FAIL ]
  Analysis:       [ PASS / FAIL ]

OVERALL: [ PASS / FAIL ]

Notes:
_____________________________________________
_____________________________________________
_____________________________________________
```

---

**Good luck with testing! 🚀**