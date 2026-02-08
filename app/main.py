"""
Main application entry point
Orchestrates scraping and data ingestion pipeline
"""
import sys
from datetime import datetime

from app.config import settings
from app.utils import setup_logging, get_logger
from app.database import DatabaseConnection
from app.scraper import EcommerceScraper
from app.services import DataIngestService

from app.services.export_service import ExportService
from app.services.transform_service import TransformService
from app.database.models import Product, TransformedProduct


def run_pipeline():
    """Run the complete scraping and ingestion pipeline"""
    
    # Setup logging
    setup_logging(
        log_level=settings.logging.level,
        log_file=settings.logging.log_file,
        log_dir=settings.logging.log_dir
    )
    
    logger = get_logger(__name__)
    
    # --- PERBAIKAN: Inisialisasi service di sini agar tersedia di seluruh fungsi ---
    ingest_service = DataIngestService()
    transform_service = TransformService()
    export_service = ExportService()
    # ------------------------------------------------------------------------------

    logger.info("=" * 80)
    logger.info("DATA ENGINEERING SCRAPING PROJECT")
    logger.info("=" * 80)
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Target: {settings.scraping.full_url}")
    logger.info(f"Max pages: {settings.scraping.max_pages}")
    logger.info("=" * 80)
    
    try:
        # 1. Database & Scraping Setup
        settings.validate()
        if not DatabaseConnection.test_connection():
            raise Exception("Database connection failed")
    
        DatabaseConnection.init_db() 
        
        scraper = EcommerceScraper(
            base_url=settings.scraping.base_url,
            category=settings.scraping.target_category,
            max_pages=settings.scraping.max_pages,
            timeout=settings.scraping.request_timeout,
            delay=settings.scraping.request_delay
        )
        
        # Run scraping
        products = scraper.scrape()
        
        if not products:
            logger.warning("No products scraped. Exiting.")
            return

        # 2. INGESTION PHASE - RAW SCHEMA
        logger.info("-" * 80)
        logger.info("Ingesting data to RAW schema...")
        ingest_service.ingest_products(
            products=products,
            model_class=Product, 
            url=settings.scraping.full_url
        )

        # 3. TRANSFORMATION PHASE
        logger.info("-" * 80)
        logger.info("Starting data transformation...")
        transformed_products = transform_service.transform_products([p.copy() for p in products])
        logger.info("✓ Data transformation completed")
        
        # 4. INGESTION PHASE - TRANSFORMED SCHEMA
        logger.info("-" * 80)
        logger.info("Ingesting data to TRANSFORMED schema...")
        stats = ingest_service.ingest_products(
            products=transformed_products,
            model_class=TransformedProduct,
            url=settings.scraping.full_url
        )
        
        # 5. EXPORT PHASE
        logger.info("-" * 80)
        # logger.info("Starting data export...")
        # csv_path = export_service.to_csv(transformed_products)
        # Di dalam main.py, panggil setelah proses ingestion raw selesai
        logger.info("Exporting RAW data to CSV...")
        raw_csv_path = export_service.to_csv(products, prefix="raw")
        logger.info(f"✓ RAW data exported to CSV at {raw_csv_path}")


        # Di dalam main.py, panggil setelah proses transformation/ingestion transformed selesai
        logger.info("Exporting TRANSFORMED data to CSV...")
        trans_csv_path = export_service.to_csv(transformed_products, prefix="transformed")
        logger.info(f"✓ TRANSFORMED data exported to CSV at {trans_csv_path}")


        # Summary Results
        logger.info("-" * 80)
        logger.info(f"Results:")
        logger.info(f"  - Total products processed: {stats['total']}")
        logger.info(f"  - Successfully inserted: {stats['inserted']}")
        logger.info(f"  - Duplicates skipped: {stats['duplicates']}")
        logger.info(f"  - Errors: {stats['errors']}")
        logger.info(f"  - Session ID: {stats['session_id']}")
        logger.info("-" * 80)

        # Get total count in database (dari schema raw untuk monitoring)
        total_in_db = ingest_service.get_product_count()
        logger.info(f"Total products in RAW database: {total_in_db}")

        scraper.close()
        
        logger.info("=" * 80)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)
        
    except KeyboardInterrupt:
        logger.warning("\nPipeline interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}", exc_info=True)
        sys.exit(1)
        
    finally:
        # Cleanup
        logger.info("Cleaning up resources...")
        DatabaseConnection.close()
        logger.info("✓ Resources cleaned up")


if __name__ == "__main__":
    run_pipeline()