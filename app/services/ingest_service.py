"""
Data ingestion service for loading scraped data into database
"""
from typing import List, Dict
from datetime import datetime
import uuid
import pytz

from sqlalchemy.exc import IntegrityError

from app.database import get_db_session, Product, ScrapingLog
from app.utils import LoggerMixin


class DataIngestService(LoggerMixin):
    """Service for ingesting scraped data into database"""
    
    def __init__(self):
        """Initialize data ingest service"""
        self.session_id = str(uuid.uuid4())[:8]
    
    def _create_scraping_log(
        self,
        url: str,
        status: str,
        records_scraped: int = 0,
        error_message: str = None,
        started_at: datetime = None,
        completed_at: datetime = None
    ) -> ScrapingLog:
        """
        Create a scraping log entry
        
        Args:
            url: URL that was scraped
            status: Status of scraping (SUCCESS, FAILED, PARTIAL)
            records_scraped: Number of records scraped
            error_message: Error message if any
            started_at: Start time
            completed_at: Completion time
            
        Returns:
            ScrapingLog object
        """
        duration = None
        if started_at and completed_at:
            duration = (completed_at - started_at).total_seconds()
        
        log = ScrapingLog(
            scrape_session_id=self.session_id,
            url=url,
            status=status,
            records_scraped=records_scraped,
            error_message=error_message,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration
        )
        
        return log
    
    def ingest_products(
        self,
        products: List[Dict],
        model_class,
        url: str
    ) -> Dict[str, int]:
        """
        Ingest product data into database
        
        Args:
            products: List of product dictionaries
            url: Source URL
            
        Returns:
            Dictionary with ingestion statistics
        """
        started_at = datetime.now(pytz.UTC)
        inserted_count = 0
        duplicate_count = 0
        error_count = 0
        
        self.logger.info(f"Starting data ingestion for {len(products)} products")
        self.logger.info(f"Session ID: {self.session_id}")
        
        try:
            with get_db_session() as session:
                for product_data in products:
                    # Gunakan savepoint untuk setiap produk
                    savepoint = session.begin_nested() 
                    try:
                        product = model_class(**product_data)
                        session.add(product)
                        session.flush()  # Cek apakah ada constraint violation
                        inserted_count += 1
                        # Savepoint otomatis 'released' saat sukses (tergantung versi, tapi aman)
                    except IntegrityError:
                        savepoint.rollback()  # HANYA membatalkan satu produk ini
                        duplicate_count += 1
                        self.logger.debug(f"Duplicate skipped: {product_data.get('product_name')}")
                    except Exception as e:
                        savepoint.rollback() # Membatalkan satu produk yang error
                        error_count += 1
                        self.logger.error(f"Error inserting product: {e}")
                
                # Commit all products
                session.commit()
                
            # Cari dictionary schema di dalam __table_args__ secara dinamis
            current_schema = None
            if hasattr(model_class, '__table_args__'):
                for arg in model_class.__table_args__:
                    if isinstance(arg, dict) and 'schema' in arg:
                        current_schema = arg.get('schema')
                        break
            
            # Logika Log: Hanya catat ke scraping_logs jika schema-nya adalah 'raw'
            if current_schema == 'raw':
                self._create_scraping_log(
                    url=url,
                    status="SUCCESS" if error_count == 0 else "PARTIAL",
                    records_scraped=inserted_count,
                    started_at=started_at,
                    completed_at=datetime.now(pytz.UTC)
                )
            # ---------------------------------------
                
            self.logger.info(f"Data ingestion completed successfully")
            self.logger.info(f"Inserted: {inserted_count}, Duplicates: {duplicate_count}, Errors: {error_count}")
                
        except Exception as e:
            self.logger.error(f"Critical error during ingestion: {e}")
            
            # Create failure log
            completed_at = datetime.now(pytz.UTC)
            try:
                with get_db_session() as session:
                    log = self._create_scraping_log(
                        url=url,
                        status='FAILED',
                        records_scraped=inserted_count,
                        error_message=str(e),
                        started_at=started_at,
                        completed_at=completed_at
                    )
                    session.add(log)
                    session.commit()
            except Exception as log_error:
                self.logger.error(f"Failed to create error log: {log_error}")
            
            raise
        
        return {
            'inserted': inserted_count,
            'duplicates': duplicate_count,
            'errors': error_count,
            'total': len(products),
            'session_id': self.session_id
        }
    
    def get_scraping_history(self, limit: int = 10) -> List[Dict]:
        """
        Get scraping history from logs
        
        Args:
            limit: Number of recent logs to retrieve
            
        Returns:
            List of log dictionaries
        """
        try:
            with get_db_session() as session:
                logs = session.query(ScrapingLog)\
                    .order_by(ScrapingLog.started_at.desc())\
                    .limit(limit)\
                    .all()
                
                return [log.to_dict() for log in logs]
                
        except Exception as e:
            self.logger.error(f"Error retrieving scraping history: {e}")
            return []
    
    def get_product_count(self) -> int:
        """
        Get total product count in database
        
        Returns:
            Total number of products
        """
        try:
            with get_db_session() as session:
                count = session.query(Product).count()
                return count
        except Exception as e:
            self.logger.error(f"Error getting product count: {e}")
            return 0