"""
Database connection management
"""
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager

from app.config import settings
from app.utils import get_logger

from .models import Base

logger = get_logger(__name__)


class DatabaseConnection:
    """Database connection manager"""
    
    _engine: Engine = None
    _session_factory = None
    
    @classmethod
    def get_engine(cls) -> Engine:
        """
        Get or create database engine
        
        Returns:
            SQLAlchemy Engine instance
        """
        if cls._engine is None:
            logger.info(f"Creating database engine for {settings.database.name}")
            cls._engine = create_engine(
                settings.database.connection_string,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,  # Verify connections before using
                echo=False  # Set to True for SQL query logging
            )
            logger.info("Database engine created successfully")
        return cls._engine
    
    @classmethod
    def get_session_factory(cls):
        """Get or create session factory"""
        if cls._session_factory is None:
            cls._session_factory = sessionmaker(
                bind=cls.get_engine(),
                autocommit=False,
                autoflush=False
            )
        return cls._session_factory
    
    @classmethod
    @contextmanager
    def get_session(cls) -> Generator[Session, None, None]:
        """
        Context manager for database sessions
        
        Yields:
            SQLAlchemy Session
        """
        session = cls.get_session_factory()()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    @classmethod
    def test_connection(cls) -> bool:
        """
        Test database connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            engine = cls.get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    @classmethod
    def close(cls):
        """Close database engine"""
        if cls._engine is not None:
            cls._engine.dispose()
            cls._engine = None
            cls._session_factory = None
            logger.info("Database engine closed")
    # @classmethod
    # def init_db(cls):
    #     """Memastikan schema 'raw' dan semua tabel tersedia"""
    #     engine = cls.get_engine()
    #     with engine.begin() as conn:
    #         # 1. Buat schema 'raw' secara manual
    #         conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
    #         # 2. Buat semua tabel yang terdefinisi di models.py
    #         Base.metadata.create_all(conn)
    #     logger.info("✓ Database schema and tables validated/created")
    @classmethod
    def init_db(cls):
        engine = cls.get_engine()
        with engine.begin() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS transformed"))
            Base.metadata.create_all(conn)
        logger.info("✓ Schemas 'raw' and 'transformed' are ready")


# Convenience functions
def get_db_engine() -> Engine:
    """Get database engine"""
    return DatabaseConnection.get_engine()


def get_db_session() -> Generator[Session, None, None]:
    """Get database session"""
    return DatabaseConnection.get_session()