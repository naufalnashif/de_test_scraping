"""
Database models using SQLAlchemy ORM
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, 
    DateTime, UniqueConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Product(Base):
    """Product model for raw scraped data"""
    
    __tablename__ = 'products'
    __table_args__ = (
        UniqueConstraint('product_name', 'description', 'price','page_number', 'scraped_at', name='unique_product_scrape'),
        Index('idx_products_category', 'category'),
        Index('idx_products_scraped_at', 'scraped_at'),
        Index('idx_products_price', 'price'),
        {'schema': 'raw'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(500), nullable=False)
    price = Column(Numeric(10, 2))
    description = Column(Text)
    rating = Column(Integer)
    review_count = Column(Integer)
    image_url = Column(Text)
    product_url = Column(Text)
    category = Column(String(200))
    page_number = Column(Integer)
    scraped_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.product_name}', price={self.price})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'product_name': self.product_name,
            'price': float(self.price) if self.price else None,
            'description': self.description,
            'rating': self.rating,
            'review_count': self.review_count,
            'image_url': self.image_url,
            'product_url': self.product_url,
            'category': self.category,
            'page_number': self.page_number,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None
        }
    
class TransformedProduct(Base):
    """Product model for transformed scraped data"""
    
    __tablename__ = 'products_transformed'
    __table_args__ = (
        UniqueConstraint('product_name', 'description', 'price','page_number', 'scraped_at', name='unique_product_scrape'),
        Index('idx_products_category', 'category'),
        Index('idx_products_scraped_at', 'scraped_at'),
        Index('idx_products_price', 'price'),
        {'schema': 'transformed'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(500), nullable=False)
    price = Column(Numeric(10, 2))
    description = Column(Text)
    rating = Column(Integer)
    review_count = Column(Integer)
    image_url = Column(Text)
    product_url = Column(Text)
    category = Column(String(200))
    page_number = Column(Integer)
    scraped_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    # --- TAMBAHAN TRANSFORMASI DATA -----
    brand = Column(String(100))
    os = Column(String(100))
    hdd = Column(String(100))
    screen_size = Column(String(50))
    display_type = Column(String(100))
    graphics_card = Column(String(200))
    processor = Column(String(200))
    
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.product_name}', price={self.price})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'product_name': self.product_name,
            'brand': self.brand, # Tambahan
            'price': float(self.price) if self.price else None,
            'description': self.description,
            'os': self.os, # Tambahan
            'hdd': self.hdd, # Tambahan
            'screen_size': self.screen_size, # Tambahan
            'display_type': self.display_type, # Tambahan
            'graphics_card': self.graphics_card, # Tambahan
            'processor': self.processor, # Tambahan
            'rating': self.rating,
            'review_count': self.review_count,
            'image_url': self.image_url,
            'product_url': self.product_url,
            'category': self.category,
            'page_number': self.page_number,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None
        }


class ScrapingLog(Base):
    """Scraping log model for tracking scraping sessions"""
    
    __tablename__ = 'scraping_logs'
    __table_args__ = (
        Index('idx_scraping_logs_session', 'scrape_session_id'),
        {'schema': 'raw'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scrape_session_id = Column(String(100), nullable=False)
    url = Column(Text)
    status = Column(String(50))
    records_scraped = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Numeric(10, 2))
    
    def __repr__(self):
        return f"<ScrapingLog(id={self.id}, session='{self.scrape_session_id}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'scrape_session_id': self.scrape_session_id,
            'url': self.url,
            'status': self.status,
            'records_scraped': self.records_scraped,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_seconds': float(self.duration_seconds) if self.duration_seconds else None
        }