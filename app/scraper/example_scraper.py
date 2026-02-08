"""
E-commerce scraper implementation
Scrapes laptop products from webscraper.io test site
"""
from typing import List, Dict, Optional
from datetime import datetime
import pytz
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper


class EcommerceScraper(BaseScraper):
    """Scraper for e-commerce laptop products"""
    
    def __init__(
        self,
        base_url: str,
        category: str = "computers/laptops",
        max_pages: int = 20,
        timeout: int = 30,
        delay: float = 1.0
    ):
        """
        Initialize e-commerce scraper
        
        Args:
            base_url: Base URL for the e-commerce site
            category: Product category to scrape
            max_pages: Maximum number of pages to scrape
            timeout: Request timeout in seconds
            delay: Delay between requests in seconds
        """
        super().__init__(base_url, timeout, delay)
        self.category = category
        self.max_pages = max_pages
        self.scrape_time = datetime.now(pytz.UTC)
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """
        Extract numeric price from text
        
        Args:
            price_text: Price text (e.g., "$499.99")
            
        Returns:
            Float price or None
        """
        try:
            # Remove currency symbols and whitespace
            clean_price = price_text.replace('$', '').replace(',', '').strip()
            return float(clean_price)
        except (ValueError, AttributeError):
            self.logger.warning(f"Could not parse price: {price_text}")
            return None
    
    def _extract_rating(self, rating_element) -> Optional[int]:
        """
        Extract rating from star elements
        
        Args:
            rating_element: BeautifulSoup element containing rating
            
        Returns:
            Integer rating (1-5) or None
        """
        try:
            if rating_element:
                # Count filled stars
                stars = rating_element.find_all('span', class_='ws-icon-star')
                return len(stars)
            return None
        except Exception as e:
            self.logger.warning(f"Could not parse rating: {e}")
            return None
    
    def _extract_review_count(self, review_text: str) -> Optional[int]:
        """
        Extract review count from text
        
        Args:
            review_text: Review text (e.g., "12 reviews")
            
        Returns:
            Integer review count or None
        """
        try:
            # Extract number from text
            count_str = review_text.split()[0].strip()
            return int(count_str)
        except (ValueError, AttributeError, IndexError):
            self.logger.warning(f"Could not parse review count: {review_text}")
            return None
    
    def parse_page(self, soup: BeautifulSoup, page_number: int) -> List[Dict]:
        """
        Parse a single page and extract product data
        
        Args:
            soup: BeautifulSoup object of the page
            page_number: Current page number
            
        Returns:
            List of product dictionaries
        """
        products = []
        
        # Find all product cards
        product_cards = soup.find_all('div', class_='card-body')
        
        self.logger.info(f"Found {len(product_cards)} products on page {page_number}")
        
        for card in product_cards:
            try:
                # Extract product name
                title_elem = card.find('a', class_='title')
                product_name = title_elem.get('title', '').strip() if title_elem else None
                product_url = title_elem.get('href', '') if title_elem else None
                
                # Extract price
                price_elem = card.find('h4', class_='price')
                price_text = price_elem.text.strip() if price_elem else None
                price = self._extract_price(price_text) if price_text else None
                
                # Extract description
                desc_elem = card.find('p', class_='description')
                description = desc_elem.text.strip() if desc_elem else None
                
                # Extract image URL
                img_elem = card.find('img', class_='image')
                image_url = img_elem.get('src', '') if img_elem else None
                
                # Extract rating
                rating_elem = card.find('p', {'data-rating': True})
                rating = self._extract_rating(rating_elem)
                
                # Extract review count
                review_elem = card.find('p', class_='review-count')
                review_count = None
                if review_elem:
                    review_span = review_elem.find('span', itemprop='reviewCount')
                    if review_span:
                        review_count = self._extract_review_count(review_span.text + ' reviews')
                
                # Create product dictionary
                product = {
                    'product_name': product_name,
                    'price': price,
                    'description': description,
                    'rating': rating,
                    'review_count': review_count,
                    'image_url': image_url,
                    'product_url': product_url,
                    'category': self.category,
                    'page_number': page_number,
                    'scraped_at': self.scrape_time
                }
                
                # Only add if we have at least a name
                if product_name:
                    products.append(product)
                    self.logger.debug(f"Extracted: {product_name} - ${price}")
                
            except Exception as e:
                self.logger.error(f"Error parsing product card: {e}")
                continue
        
        return products
    
    def scrape(self) -> List[Dict]:
        """
        Scrape all pages and collect product data
        
        Returns:
            List of all scraped products
        """
        all_products = []
        
        self.logger.info(f"Starting scrape for category: {self.category}")
        self.logger.info(f"Maximum pages to scrape: {self.max_pages}")
        
        for page_num in range(1, self.max_pages + 1):
            # Construct page URL
            if page_num == 1:
                url = f"{self.base_url}/{self.category}"
            else:
                url = f"{self.base_url}/{self.category}?page={page_num}"
            
            # Fetch and parse page
            soup = self.fetch_page(url)
            
            if soup is None:
                self.logger.warning(f"Failed to fetch page {page_num}, stopping scrape")
                break
            
            # Extract products from page
            products = self.parse_page(soup, page_num)
            
            if not products:
                self.logger.info(f"No products found on page {page_num}, stopping scrape")
                break
            
            all_products.extend(products)
            self.logger.info(f"Page {page_num}: Scraped {len(products)} products")
        
        self.logger.info(f"Scraping completed. Total products: {len(all_products)}")
        
        return all_products