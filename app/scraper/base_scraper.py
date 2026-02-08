"""
Base scraper class with common scraping functionality
"""
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

from app.utils import LoggerMixin


class BaseScraper(ABC, LoggerMixin):
    """Abstract base class for web scrapers"""
    
    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        delay: float = 1.0
    ):
        """
        Initialize base scraper
        
        Args:
            base_url: Base URL for scraping
            timeout: Request timeout in seconds
            delay: Delay between requests in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.delay = delay
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create requests session with headers"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        return session
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a web page
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            self.logger.info(f"Fetching URL: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            self.logger.info(f"Successfully fetched and parsed: {url}")
            
            # Respect rate limiting
            time.sleep(self.delay)
            
            return soup
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error parsing {url}: {e}")
            return None
    
    @abstractmethod
    def parse_page(self, soup: BeautifulSoup, page_number: int) -> List[Dict]:
        """
        Parse a page and extract data
        
        Args:
            soup: BeautifulSoup object
            page_number: Current page number
            
        Returns:
            List of extracted data dictionaries
        """
        pass
    
    @abstractmethod
    def scrape(self) -> List[Dict]:
        """
        Main scraping method
        
        Returns:
            List of all scraped data
        """
        pass
    
    def close(self):
        """Close the requests session"""
        if self.session:
            self.session.close()
            self.logger.info("Scraper session closed")