"""
Application settings and configuration management
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str
    port: int
    name: str
    user: str
    password: str
    
    @property
    def connection_string(self) -> str:
        """Generate PostgreSQL connection string"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class ScrapingConfig:
    """Scraping configuration"""
    base_url: str
    target_category: str
    max_pages: int
    request_timeout: int
    request_delay: float
    
    @property
    def full_url(self) -> str:
        """Generate full target URL"""
        return f"{self.base_url}/{self.target_category}"


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str
    log_file: str
    log_dir: str = "logs"
    
    @property
    def log_path(self) -> str:
        """Generate full log file path"""
        return os.path.join(self.log_dir, self.log_file)


class Settings:
    """Application settings manager"""
    
    def __init__(self):
        """Initialize settings from environment variables"""
        self.database = DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432)),
            name=os.getenv("DB_NAME", "de_test_danone"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "")
        )
        
        self.scraping = ScrapingConfig(
            base_url=os.getenv("BASE_URL", "https://webscraper.io/test-sites/e-commerce/static"),
            target_category=os.getenv("TARGET_CATEGORY", "computers/laptops"),
            max_pages=int(os.getenv("MAX_PAGES", 20)),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", 30)),
            request_delay=float(os.getenv("REQUEST_DELAY", 1.0))
        )
        
        self.logging = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "app.log")
        )
    
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.database.password:
            raise ValueError("Database password is required")
        if self.scraping.max_pages < 1:
            raise ValueError("max_pages must be at least 1")
        return True


# Global settings instance
settings = Settings()