from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from contextlib import contextmanager
from typing import Generator
import logging
from sqlalchemy.exc import OperationalError
from .models import Base, Article, Source

# Configure logging
logger = logging.getLogger(__name__)

# Get database URL from environment variable
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///news.db')  # Use SQLite for local development

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db() -> Generator:
    """
    Context manager for database sessions.
    Usage:
        with get_db() as db:
            # Use db session here
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables and run migrations"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Check existing tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        logger.info(f"Existing tables: {existing_tables}")
        
        if 'articles' in existing_tables and 'sources' in existing_tables:
            logger.info("Tables already exist, skipping initialization.")
            
            # Run migrations
            with get_db() as db:
                # Check if region column exists and remove it
                try:
                    result = db.execute(text("PRAGMA table_info(articles)"))
                    columns = [row[1] for row in result.fetchall()]
                    
                    if 'region' in columns:
                        logger.info("Removing deprecated region column")
                        db.execute(text("ALTER TABLE articles DROP COLUMN region"))
                        
                    if 'region_match' in columns:
                        logger.info("Removing deprecated region_match column")
                        db.execute(text("ALTER TABLE articles DROP COLUMN region_match"))
                        
                    # Add topics column if it doesn't exist
                    if 'topics' not in columns:
                        logger.info("Adding topics column")
                        db.execute(text("ALTER TABLE articles ADD COLUMN topics TEXT"))
                        
                    db.commit()
                    logger.info("Database migrations completed successfully")
                    
                except Exception as e:
                    logger.warning(f"Migration error (may be expected): {e}")
                    db.rollback()
        else:
            logger.info("Creating new database tables")
            
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise

def get_db_session():
    """Get a database session"""
    engine, Session = init_db()
    return Session() 