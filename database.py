"""
Database initialization and migration utilities
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Base
from app.config import settings


def init_database():
    """Initialize database and create tables"""
    engine = create_engine(settings.DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("✓ Database initialized successfully")
    print(f"  Database: {settings.DATABASE_URL}")
    
    return engine


def get_session_factory():
    """Get database session factory"""
    engine = create_engine(settings.DATABASE_URL)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


if __name__ == "__main__":
    init_database()
