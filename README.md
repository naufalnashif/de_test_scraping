# Data Engineering Scraping Project

Professional web scraping application for e-commerce data ingestion with PostgreSQL database storage and Docker deployment.

## 📋 Project Overview

This project scrapes laptop product data from [webscraper.io test site](https://webscraper.io/test-sites/e-commerce/static/computers/laptops) and stores it in a PostgreSQL database. It includes:

- **Web Scraping**: Automated data collection from e-commerce website
- **Data Storage**: PostgreSQL database with raw and processed schemas
- **Logging**: Comprehensive file and console logging
- **Docker**: Containerized deployment with docker-compose
- **Data Exploration**: Jupyter notebook for data analysis
- **Professional Structure**: Clean, maintainable code architecture

## 🏗️ Project Structure

```
data-engineer-scraping-project/
│
├── app/                          # Main application code
│   ├── __init__.py
│   ├── main.py                   # Entry point
│   │
│   ├── config/                   # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py          # Settings from environment
│   │
│   ├── database/                 # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py        # Database connection management
│   │   └── models.py            # SQLAlchemy ORM models
│   │
│   ├── scraper/                  # Web scraping logic
│   │   ├── __init__.py
│   │   ├── base_scraper.py      # Base scraper class
│   │   └── example_scraper.py   # E-commerce scraper implementation
│   │
│   ├── services/                 # Business logic services
│   │   ├── __init__.py
│   │   └── ingest_service.py    # Data ingestion service
│   │
│   └── utils/                    # Utility modules
│       ├── __init__.py
│       └── logger.py            # Logging configuration
│
├── notebooks/                    # Jupyter notebooks
│   └── exploration.ipynb        # Data exploration and analysis
│
├── scripts/                      # Database scripts
│   └── init_db.sql             # Database initialization
│
├── logs/                         # Application logs (auto-generated)
│
├── .env                         # Environment variables
├── .env.example                 # Environment template
├── Dockerfile                   # Docker image definition
├── docker-compose.yml           # Docker services orchestration
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🚀 Features

### 1. Web Scraping
- Extracts product information: name, price, description, rating, reviews
- Handles pagination automatically
- Respects rate limiting with configurable delays
- Robust error handling and retry logic
- Timestamp tracking for each scrape

### 2. Database Storage
- **Raw Schema**: Stores raw scraped data with full history
- **Processed Schema**: Stores cleaned and deduplicated data
- **Views**: Pre-built views for latest products and statistics
- **Indexes**: Optimized for query performance
- **Logging**: Tracks all scraping sessions

### 3. Data Quality
- Duplicate detection and handling
- Missing value tracking
- Data validation
- Scraping session logs with status tracking

### 4. Logging
- Color-coded console output
- Detailed file logging
- Separate log levels for console and file
- Structured logging with timestamps

### 5. Docker Deployment
- PostgreSQL container with data persistence
- Scraper application container
- Jupyter notebook container for analysis
- Network isolation
- Health checks

## 📦 Installation & Setup

### Prerequisites
- Docker and Docker Compose installed
- OR: Python 3.11+, PostgreSQL 15+

### Option 1: Docker Deployment (Recommended)

1. **Clone or download the project**
   ```bash
   cd data-engineer-scraping-project
   ```

2. **Review and update environment variables** (optional)
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

   This will start:
   - PostgreSQL database (port 5432)
   - Scraper application (runs once and exits)
   - Jupyter notebook (port 8888)

4. **View logs**
   ```bash
   # View scraper logs
   docker-compose logs scraper
   
   # Follow logs in real-time
   docker-compose logs -f scraper
   ```

5. **Access Jupyter Notebook**
   ```
   Open browser: http://localhost:8888
   ```

6. **Run scraper again**
   ```bash
   docker-compose restart scraper
   ```

7. **Stop all services**
   ```bash
   docker-compose down
   ```

### Option 2: Local Development

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup PostgreSQL database**
   ```bash
   # Create database
   createdb de_test_danone
   
   # Initialize schema
   psql -d de_test_danone -f scripts/init_db.sql
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Run the scraper**
   ```bash
   python app/main.py
   ```

5. **Start Jupyter notebook**
   ```bash
   jupyter notebook
   ```

## 💾 Database Schema

### Raw Schema (`raw`)

**Table: `raw.products`**
- `id`: Serial primary key
- `product_name`: Product name (varchar 500)
- `price`: Product price (numeric)
- `description`: Product description (text)
- `rating`: Star rating (integer 1-5)
- `review_count`: Number of reviews (integer)
- `image_url`: Product image URL (text)
- `product_url`: Product page URL (text)
- `category`: Product category (varchar 200)
- `page_number`: Source page number (integer)
- `scraped_at`: Timestamp of scraping (timestamptz)

**Table: `raw.scraping_logs`**
- `id`: Serial primary key
- `scrape_session_id`: Unique session identifier
- `url`: URL scraped
- `status`: SUCCESS/FAILED/PARTIAL
- `records_scraped`: Number of records collected
- `error_message`: Error details if failed
- `started_at`: Session start time
- `completed_at`: Session end time
- `duration_seconds`: Duration in seconds

### Processed Schema (`processed`)

**Table: `processed.products_clean`**
- Cleaned and deduplicated products
- Includes additional analytics fields

**Views:**
- `processed.latest_products`: Latest version of each product
- `processed.product_statistics`: Aggregated statistics by category

## 📊 Data Analysis

### Using Jupyter Notebook

The `notebooks/exploration.ipynb` notebook provides:

1. **Database Connection**: Connect to PostgreSQL
2. **Data Overview**: Table sizes, record counts
3. **Data Quality**: Missing values, duplicates
4. **Price Analysis**: Distribution, ranges, statistics
5. **Rating Analysis**: Rating distribution, correlation with price
6. **Review Analysis**: Review counts, top reviewed products
7. **SQL Queries**: Advanced analysis using raw SQL
8. **Data Export**: Export results to CSV
9. **Summary Report**: Comprehensive analysis summary

### Sample Queries

```sql
-- Top 10 most expensive products
SELECT product_name, price, rating, review_count
FROM raw.products
ORDER BY price DESC
LIMIT 10;

-- Average price by rating
SELECT rating, ROUND(AVG(price)::numeric, 2) as avg_price
FROM raw.products
GROUP BY rating
ORDER BY rating;

-- Products with best value (high rating, low price)
SELECT product_name, price, rating, review_count
FROM raw.products
WHERE rating >= 4 AND review_count >= 5
ORDER BY price ASC
LIMIT 10;

-- Scraping session history
SELECT scrape_session_id, records_scraped, duration_seconds, status
FROM raw.scraping_logs
ORDER BY started_at DESC;
```

## 🔧 Configuration

Edit `.env` file to customize:

```env
# Database
DB_HOST=dummy          # Use 'db' in Docker
DB_PORT=dummy
DB_NAME=dummy
DB_USER=postgres
DB_PASSWORD=postgres

# Scraping
BASE_URL=https://webscraper.io/test-sites/e-commerce/static
TARGET_CATEGORY=computers/laptops
MAX_PAGES=20              # Maximum pages to scrape
REQUEST_TIMEOUT=30        # Request timeout in seconds
REQUEST_DELAY=1           # Delay between requests (seconds)

# Logging
LOG_LEVEL=INFO           # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=app.log
```

## 📝 Logs

Logs are stored in the `logs/` directory:

- **Console Output**: Color-coded, INFO level and above
- **File Output**: Detailed logs including DEBUG level
- **Format**: `timestamp - logger - level - message`

Example log output:
```
2026-02-07 10:30:15 - __main__ - INFO - Starting web scraping...
2026-02-07 10:30:16 - EcommerceScraper - INFO - Fetching URL: https://webscraper.io/...
2026-02-07 10:30:17 - EcommerceScraper - INFO - Page 1: Scraped 9 products
2026-02-07 10:30:45 - DataIngestService - INFO - Data ingestion completed successfully
```

## 🧪 Testing

Test database connection:
```python
from app.database import DatabaseConnection
DatabaseConnection.test_connection()
```

Test scraper:
```python
from app.scraper import EcommerceScraper
scraper = EcommerceScraper(base_url="...", max_pages=1)
products = scraper.scrape()
print(f"Scraped {len(products)} products")
```

## 🐛 Troubleshooting

### Database Connection Failed
- Check PostgreSQL is running: `docker-compose ps`
- Verify credentials in `.env`
- Check database exists: `psql -l`

### No Products Scraped
- Check internet connection
- Verify target URL is accessible
- Review logs for error messages
- Increase `REQUEST_TIMEOUT`

### Docker Issues
- Clean up: `docker-compose down -v`
- Rebuild: `docker-compose build --no-cache`
- Check logs: `docker-compose logs`

### Permission Errors (logs folder)
```bash
chmod -R 755 logs/
```

## 📈 Performance

- **Scraping Speed**: ~1 page per second (with 1s delay)
- **Database Inserts**: ~100 products per second
- **Memory Usage**: <100MB for scraper
- **Storage**: ~10KB per product record

## 🔒 Security Notes

- Never commit `.env` file to version control
- Use strong database passwords in production
- Implement rate limiting respect
- Use secure connections (SSL) in production

## 🚀 Future Enhancements

- [ ] Add data validation rules
- [ ] Implement incremental scraping
- [ ] Add email notifications on completion
- [ ] Create REST API for data access
- [ ] Add unit tests
- [ ] Implement data quality dashboard
- [ ] Add support for multiple categories
- [ ] Schedule automated scraping (cron/airflow)

## 📄 License

This project is for educational and testing purposes.

## 👤 Author

Data Engineering Team - Technical Test

## 🙏 Acknowledgments

- Test site: [webscraper.io](https://webscraper.io/)
- Built for: Danone Data Engineering Assessment

---

**Last Updated**: February 2026
**Version**: 1.0.0
