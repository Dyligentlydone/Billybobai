import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

class DatabaseConfig:
    def __init__(self):
        # Get database URL from environment
        self.DATABASE_URL = os.getenv('DATABASE_URL')
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        # Handle Railway's postgres:// URL format
        if self.DATABASE_URL.startswith('postgres://'):
            self.DATABASE_URL = self.DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        
        # Configure SQLAlchemy engine with connection pooling
        self.engine = create_engine(
            self.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_pre_ping=True,  # Enable connection health checks
            echo=os.getenv('ENVIRONMENT') != 'production'  # SQL logging in non-prod
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def init_db(self):
        """Initialize database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise

    def get_db(self):
        """Get database session"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

# Create global instance
db_config = DatabaseConfig()
