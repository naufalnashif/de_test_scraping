-- Create schema for raw data
CREATE SCHEMA IF NOT EXISTS raw;

-- Create schema for processed data
CREATE SCHEMA IF NOT EXISTS processed;

-- Create table for product scraping
CREATE TABLE IF NOT EXISTS raw.products (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(500),
    price DECIMAL(10, 2),
    description TEXT,
    rating INTEGER,
    review_count INTEGER,
    image_url TEXT,
    product_url TEXT,
    category VARCHAR(200),
    page_number INTEGER,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_product_scrape UNIQUE (product_name, scraped_at)
);

-- Create table for scraping logs
CREATE TABLE IF NOT EXISTS raw.scraping_logs (
    id SERIAL PRIMARY KEY,
    scrape_session_id VARCHAR(100),
    url TEXT,
    status VARCHAR(50),
    records_scraped INTEGER,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds DECIMAL(10, 2)
);

-- Create processed table with cleaned data
CREATE TABLE IF NOT EXISTS processed.products_clean (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(500),
    price DECIMAL(10, 2),
    description TEXT,
    rating INTEGER,
    review_count INTEGER,
    category VARCHAR(200),
    avg_price_category DECIMAL(10, 2),
    price_rank INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_product_clean UNIQUE (product_name)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_products_category ON raw.products(category);
CREATE INDEX IF NOT EXISTS idx_products_scraped_at ON raw.products(scraped_at);
CREATE INDEX IF NOT EXISTS idx_products_price ON raw.products(price);
CREATE INDEX IF NOT EXISTS idx_scraping_logs_session ON raw.scraping_logs(scrape_session_id);
CREATE INDEX IF NOT EXISTS idx_products_clean_category ON processed.products_clean(category);

-- Create view for latest products
CREATE OR REPLACE VIEW processed.latest_products AS
SELECT DISTINCT ON (product_name)
    id,
    product_name,
    price,
    description,
    rating,
    review_count,
    category,
    scraped_at
FROM raw.products
ORDER BY product_name, scraped_at DESC;

-- Create view for product statistics
CREATE OR REPLACE VIEW processed.product_statistics AS
SELECT 
    category,
    COUNT(*) as total_products,
    AVG(price) as avg_price,
    MIN(price) as min_price,
    MAX(price) as max_price,
    AVG(rating) as avg_rating,
    SUM(review_count) as total_reviews
FROM raw.products
GROUP BY category;

COMMENT ON TABLE raw.products IS 'Raw scraped product data from e-commerce website';
COMMENT ON TABLE raw.scraping_logs IS 'Logs of scraping sessions and their results';
COMMENT ON TABLE processed.products_clean IS 'Cleaned and deduplicated product data';