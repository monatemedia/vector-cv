"""
Migration script to add block_type and priority columns to existing database.
Run this BEFORE running the updated seed_data.py
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def migrate_database():
    print("Starting database migration...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # Check if columns already exist
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='experience_blocks' AND column_name='block_type'
            """))
            
            if result.fetchone():
                print("✅ Columns already exist, skipping migration")
                return
            
            # Add block_type column with default value
            print("Adding block_type column...")
            conn.execute(text("""
                ALTER TABLE experience_blocks 
                ADD COLUMN block_type VARCHAR(50) DEFAULT 'supporting_project'
            """))
            
            # Add priority column
            print("Adding priority column...")
            conn.execute(text("""
                ALTER TABLE experience_blocks 
                ADD COLUMN priority VARCHAR(10) DEFAULT '3'
            """))
            
            # Update existing records based on title patterns
            print("Categorizing existing blocks...")
            
            # Mark pillar projects
            conn.execute(text("""
                UPDATE experience_blocks 
                SET block_type = 'pillar_project', priority = '1'
                WHERE title LIKE '%ActuallyFind%' OR title LIKE '%Vector CV%'
            """))
            
            # Mark employment
            conn.execute(text("""
                UPDATE experience_blocks 
                SET block_type = 'employment', priority = '1'
                WHERE title LIKE '%Developer%' AND company = 'Monate Media'
                   OR title LIKE '%Advisor%'
                   OR title LIKE '%Insurance%'
                   OR title LIKE '%Consultant%'
            """))
            
            # Mark education
            conn.execute(text("""
                UPDATE experience_blocks 
                SET block_type = 'education', priority = '1'
                WHERE title LIKE '%Education%' OR title LIKE '%Certifications%'
            """))
            
            # Mark skills summary (if it exists)
            conn.execute(text("""
                UPDATE experience_blocks 
                SET block_type = 'skills_summary', priority = '1'
                WHERE title LIKE '%Skills%' OR title LIKE '%Technical%'
            """))
            
            conn.commit()
            print("✅ Migration completed successfully!")
            print("\nNext steps:")
            print("1. Review the categorization by running: SELECT title, block_type, priority FROM experience_blocks;")
            print("2. Manually adjust any miscategorized blocks if needed")
            print("3. Consider running seed_data.py with fresh data for optimal results")
            
        except Exception as e:
            print(f"❌ Migration error: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    migrate_database()