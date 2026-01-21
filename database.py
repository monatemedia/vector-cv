import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import Base

# Load environment variables from .env
load_dotenv()

def get_database_url():
    """
    Dynamically build the database URL from components or returns DATABASE_URL if set.
    """
    url = os.getenv("DATABASE_URL")
    
    if not url:
        # Fallback to building from individual components
        user = os.getenv("DB_USER", "resume_user")
        password = os.getenv("DB_PASSWORD", "resume_pass")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "resume_db")
        
        url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    
    # SQLAlchemy 2.0 requires 'postgresql://' instead of 'postgres://'
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    
    return url

# Initialize engine with the dynamic URL
engine = create_engine(
    get_database_url(),
    # Robust connection settings
    connect_args={
        "options": "-c search_path=public",
        "connect_timeout": 10
    },
    pool_pre_ping=True  # Recommended: checks if connection is alive before using it
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database with pgvector extension and create tables"""
    try:
        with engine.connect() as conn:
            # Enable pgvector extension
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            print("✅ pgvector extension verified/installed")
            
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        raise e

def get_db():
    """Dependency for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()