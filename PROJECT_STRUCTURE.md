# Project Structure Documentation

Dokumentasi lengkap struktur project Data Engineering Scraping.

## 📂 Directory Structure

```
data-engineer-scraping-project/
│
├── 📄 README.md                      # Dokumentasi utama project
├── 📄 QUICKSTART.md                  # Panduan cepat memulai
├── 📄 PROJECT_STRUCTURE.md           # File ini - dokumentasi struktur
├── 📄 .env                           # Environment variables (JANGAN di-commit!)
├── 📄 .env.example                   # Template environment variables
├── 📄 .gitignore                     # Git ignore rules
├── 📄 Dockerfile                     # Docker image definition
├── 📄 docker-compose.yml             # Docker orchestration
├── 📄 requirements.txt               # Python dependencies
│
├── 📁 app/                           # ⭐ Main application code
│   ├── 📄 __init__.py
│   ├── 📄 main.py                    # 🚀 Entry point aplikasi
│   │
│   ├── 📁 config/                    # Konfigurasi aplikasi
│   │   ├── 📄 __init__.py
│   │   └── 📄 settings.py            # Settings dari environment variables
│   │
│   ├── 📁 database/                  # Layer database
│   │   ├── 📄 __init__.py
│   │   ├── 📄 connection.py          # Database connection management
│   │   └── 📄 models.py              # SQLAlchemy ORM models
│   │
│   ├── 📁 scraper/                   # Web scraping logic
│   │   ├── 📄 __init__.py
│   │   ├── 📄 base_scraper.py        # Abstract base class
│   │   └── 📄 example_scraper.py     # E-commerce scraper implementation
│   │
│   ├── 📁 services/                  # Business logic
│   │   ├── 📄 __init__.py
│   │   └── 📄 ingest_service.py      # Data ingestion service
│   │
│   └── 📁 utils/                     # Utilities
│       ├── 📄 __init__.py
│       └── 📄 logger.py               # Logging configuration
│
├── 📁 notebooks/                     # Jupyter notebooks untuk analisis
│   └── 📓 exploration.ipynb          # Data exploration notebook
│
├── 📁 scripts/                       # Database scripts
│   └── 📄 init_db.sql                # Database initialization script
│
└── 📁 logs/                          # Application logs (auto-generated)
    └── 📄 app.log                    # Main log file
```

## 🔍 File Details

### Core Application Files

#### `app/main.py` 🚀
**Purpose**: Entry point aplikasi
**Description**: 
- Orchestrasi pipeline scraping dan ingestion
- Setup logging
- Validasi konfigurasi
- Koordinasi scraper dan database service

**Key Functions**:
- `run_pipeline()`: Main orchestrator

**Usage**:
```bash
python app/main.py
```

---

#### `app/config/settings.py` ⚙️
**Purpose**: Manajemen konfigurasi
**Description**:
- Load environment variables dari `.env`
- Provide konfigurasi terstruktur untuk semua module
- Validasi konfigurasi

**Classes**:
- `DatabaseConfig`: Konfigurasi database
- `ScrapingConfig`: Konfigurasi scraping
- `LoggingConfig`: Konfigurasi logging
- `Settings`: Main settings manager

**Usage**:
```python
from app.config import settings
print(settings.database.connection_string)
```

---

#### `app/database/connection.py` 💾
**Purpose**: Database connection management
**Description**:
- Singleton pattern untuk database engine
- Connection pooling
- Session management dengan context manager
- Health check

**Classes**:
- `DatabaseConnection`: Main connection manager

**Key Methods**:
- `get_engine()`: Get SQLAlchemy engine
- `get_session()`: Context manager untuk session
- `test_connection()`: Test koneksi database

**Usage**:
```python
from app.database import get_db_session

with get_db_session() as session:
    # Your database operations
    pass
```

---

#### `app/database/models.py` 📋
**Purpose**: ORM models
**Description**:
- SQLAlchemy models untuk tabel database
- Relationship definitions
- Helper methods

**Models**:
- `Product`: Model untuk raw.products
- `ScrapingLog`: Model untuk raw.scraping_logs

**Usage**:
```python
from app.database import Product
from app.database import get_db_session

with get_db_session() as session:
    products = session.query(Product).all()
```

---

#### `app/scraper/base_scraper.py` 🌐
**Purpose**: Base scraper class
**Description**:
- Abstract base class untuk semua scrapers
- Common functionality: fetch, parse, rate limiting
- Session management

**Classes**:
- `BaseScraper`: Abstract base class

**Key Methods**:
- `fetch_page()`: Fetch dan parse web page
- `parse_page()`: Abstract method untuk parsing
- `scrape()`: Abstract method untuk main scraping

**Usage**:
```python
class CustomScraper(BaseScraper):
    def parse_page(self, soup, page_number):
        # Implementation
        pass
    
    def scrape(self):
        # Implementation
        pass
```

---

#### `app/scraper/example_scraper.py` 🛒
**Purpose**: E-commerce scraper implementation
**Description**:
- Implementasi konkrit dari BaseScraper
- Scrape laptop products
- Handle pagination
- Extract product details

**Classes**:
- `EcommerceScraper`: E-commerce specific scraper

**Key Methods**:
- `parse_page()`: Parse product cards dari halaman
- `scrape()`: Main scraping loop
- `_extract_price()`, `_extract_rating()`: Helper methods

**Usage**:
```python
from app.scraper import EcommerceScraper

scraper = EcommerceScraper(
    base_url="https://webscraper.io/test-sites/e-commerce/static",
    category="computers/laptops",
    max_pages=5
)
products = scraper.scrape()
```

---

#### `app/services/ingest_service.py` 📥
**Purpose**: Data ingestion service
**Description**:
- Insert scraped data ke database
- Handle duplicates
- Create scraping logs
- Track statistics

**Classes**:
- `DataIngestService`: Main ingestion service

**Key Methods**:
- `ingest_products()`: Ingest product list
- `get_scraping_history()`: Get scraping logs
- `get_product_count()`: Get total products

**Usage**:
```python
from app.services import DataIngestService

service = DataIngestService()
stats = service.ingest_products(products, url)
print(f"Inserted: {stats['inserted']}")
```

---

#### `app/utils/logger.py` 📝
**Purpose**: Logging utilities
**Description**:
- Setup colorized console logging
- File logging dengan rotation
- Logger factory

**Functions**:
- `setup_logging()`: Initialize logging system
- `get_logger()`: Get logger instance

**Classes**:
- `LoggerMixin`: Mixin untuk add logging ke class

**Usage**:
```python
from app.utils import setup_logging, get_logger

setup_logging(log_level="INFO", log_file="app.log")
logger = get_logger(__name__)
logger.info("Hello, World!")
```

---

### Database Scripts

#### `scripts/init_db.sql` 🗄️
**Purpose**: Database initialization
**Description**:
- Create schemas (raw, processed)
- Create tables
- Create indexes
- Create views
- Add comments

**Tables Created**:
- `raw.products`: Raw scraped products
- `raw.scraping_logs`: Scraping session logs
- `processed.products_clean`: Cleaned products

**Views Created**:
- `processed.latest_products`: Latest version of each product
- `processed.product_statistics`: Aggregated statistics

**Usage**:
```bash
# With Docker
docker exec -i de_postgres psql -U postgres -d de_test_danone < scripts/init_db.sql

# Local
psql -d de_test_danone -f scripts/init_db.sql
```

---

### Notebooks

#### `notebooks/exploration.ipynb` 📊
**Purpose**: Data exploration and analysis
**Description**:
- Connect to database
- Load and analyze data
- Create visualizations
- Export results

**Sections**:
1. Setup & Connection
2. Data Overview
3. Data Quality Analysis
4. Price Analysis
5. Rating Analysis
6. Review Analysis
7. SQL Queries
8. Data Export
9. Summary Report

**Usage**:
```bash
# With Docker
# Access http://localhost:8888

# Local
jupyter notebook
```

---

### Configuration Files

#### `.env` 🔐
**Purpose**: Environment variables
**Description**: Menyimpan konfigurasi sensitif
**⚠️ NEVER commit to Git!**

**Variables**:
- Database credentials
- Scraping parameters
- Logging configuration

---

#### `docker-compose.yml` 🐳
**Purpose**: Docker orchestration
**Description**: Define dan coordinate multiple containers

**Services**:
- `db`: PostgreSQL database
- `scraper`: Scraping application
- `jupyter`: Jupyter notebook server

**Networks**:
- `scraper_network`: Isolated network

**Volumes**:
- `postgres_data`: Persistent database storage

---

#### `Dockerfile` 📦
**Purpose**: Docker image definition
**Description**: Define container image untuk aplikasi

**Base Image**: python:3.11-slim

**Key Steps**:
1. Install system dependencies
2. Install Python packages
3. Copy application code
4. Create logs directory
5. Set environment

---

#### `requirements.txt` 📋
**Purpose**: Python dependencies
**Description**: List semua Python packages yang diperlukan

**Main Dependencies**:
- requests, beautifulsoup4: Web scraping
- psycopg2-binary, SQLAlchemy: Database
- pandas, numpy: Data processing
- jupyter: Analysis notebooks
- colorlog: Colored logging

---

## 🔄 Data Flow

```
1. [User] → Runs `python app/main.py`
          ↓
2. [main.py] → Setup logging, validate config
          ↓
3. [DatabaseConnection] → Test connection
          ↓
4. [EcommerceScraper] → Scrape website
          ↓
5. [BaseScraper] → Fetch pages, parse HTML
          ↓
6. [EcommerceScraper] → Extract product data
          ↓
7. [DataIngestService] → Insert to database
          ↓
8. [DatabaseConnection] → Save to PostgreSQL
          ↓
9. [ScrapingLog] → Log session results
          ↓
10. [Logger] → Write logs to file/console
```

## 🎯 Module Responsibilities

### `app/config/`
- ✅ Load environment variables
- ✅ Provide configuration to other modules
- ✅ Validate configuration
- ❌ NO business logic
- ❌ NO database access

### `app/database/`
- ✅ Manage database connections
- ✅ Define ORM models
- ✅ Provide database sessions
- ❌ NO scraping logic
- ❌ NO business logic

### `app/scraper/`
- ✅ Fetch web pages
- ✅ Parse HTML
- ✅ Extract data
- ❌ NO database access
- ❌ NO file I/O (except logging)

### `app/services/`
- ✅ Business logic
- ✅ Orchestrate operations
- ✅ Handle data transformation
- ✅ Can use database and scraper
- ❌ NO direct HTTP requests

### `app/utils/`
- ✅ Utility functions
- ✅ Helper classes
- ✅ Reusable components
- ❌ NO business logic

## 🧩 Design Patterns Used

1. **Singleton Pattern**: DatabaseConnection
2. **Context Manager**: Database sessions
3. **Abstract Base Class**: BaseScraper
4. **Factory Pattern**: get_logger()
5. **Mixin Pattern**: LoggerMixin
6. **Service Pattern**: DataIngestService

## 📝 Naming Conventions

- **Classes**: PascalCase (e.g., `DatabaseConnection`)
- **Functions**: snake_case (e.g., `get_db_session`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DB_HOST`)
- **Private methods**: _leading_underscore (e.g., `_extract_price`)
- **Modules**: lowercase (e.g., `connection.py`)

## 🔒 Security Notes

- `.env` file contains credentials → **NEVER commit**
- Use `.env.example` as template
- Database password in environment variable
- No hardcoded credentials in code

---

**Last Updated**: February 2026