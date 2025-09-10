from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.models import Base
from app.services.news_simulator import initialize_sample_data
import logging

logger = logging.getLogger(__name__)

def create_database():
    """Create database tables and initialize with sample data"""
    try:
        # Create engine
        engine = create_engine(settings.database_url)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created")
        
        # Initialize sample data
        import asyncio
        asyncio.run(initialize_sample_data())
        
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise

if __name__ == "__main__":
    create_database()
