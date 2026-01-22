import os
import json
import sys
from pathlib import Path
from database import SessionLocal, engine
from models import ExperienceBlock, PersonalInfo, Base, BlockType
from llm_service import generate_embedding


def load_personal_data(json_path: str = "my_data/my_data.json") -> dict:
    """Load personal data from JSON file."""
    if not Path(json_path).exists():
        print(f"❌ Error: {json_path} not found.")
        print(f"Please create {json_path} with your personal data.")
        print(f"See my_data/my_data.json.example for the expected format.")
        sys.exit(1)
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def seed_personal_info(db, data: dict):
    """Seed or update personal information."""
    print("Seeding Personal Info...")
    
    # Check if personal info already exists
    existing = db.query(PersonalInfo).first()
    
    if existing:
        print("  → Updating existing personal info")
        for key, value in data.items():
            setattr(existing, key, value)
    else:
        print("  + Adding new personal info")
        person = PersonalInfo(**data)
        db.add(person)
    
    db.commit()


def seed_experience_blocks(db, blocks: list):
    """Seed or update experience blocks with embeddings."""
    print("Generating embeddings and saving blocks...")
    
    for item in blocks:
        # Check if this block already exists by title
        existing_block = db.query(ExperienceBlock).filter(
            ExperienceBlock.title == item['title']
        ).first()
        
        # Prepare combined text for embedding
        combined_text = (
            f"{item['title']} at {item['company']}: "
            f"{item['content']} Keywords: {', '.join(item['tags'])}"
        )
        
        if existing_block:
            print(f"  → Updating existing block: {item['title']}")
            existing_block.content = item['content']
            existing_block.metadata_tags = item['tags']
            existing_block.company = item['company']
            existing_block.block_type = BlockType(item['block_type'])
            existing_block.priority = item['priority']
            existing_block.embedding = generate_embedding(combined_text)
        else:
            print(f"  + Adding new block: {item['title']}")
            vector = generate_embedding(combined_text)
            
            block = ExperienceBlock(
                title=item['title'],
                company=item['company'],
                content=item['content'],
                metadata_tags=item['tags'],
                block_type=BlockType(item['block_type']),
                priority=item['priority'],
                embedding=vector
            )
            db.add(block)
    
    db.commit()


def print_summary(blocks: list):
    """Print summary of seeded data."""
    block_counts = {}
    for block in blocks:
        block_type = block['block_type']
        block_counts[block_type] = block_counts.get(block_type, 0) + 1
    
    print("\n✅ Seeding complete! Your RAG system is now fully optimized.")
    print(f"📚 Processed {len(blocks)} experience blocks:")
    for block_type, count in sorted(block_counts.items()):
        print(f"   - {count} {block_type.replace('_', ' ').title()}")


def seed_database(json_path: str = "my_data/my_data.json"):
    """Main seeding function."""
    print("Starting database seeding...")
    
    # Load personal data from JSON
    data = load_personal_data(json_path)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Seed personal info
        seed_personal_info(db, data['personal_info'])
        
        # Seed experience blocks
        seed_experience_blocks(db, data['experience_blocks'])
        
        # Print summary
        print_summary(data['experience_blocks'])
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    from database import init_db
    
    # Get JSON path from command line or use default
    json_path = sys.argv[1] if len(sys.argv) > 1 else "my_data/my_data.json"
    
    # Initialize database (create tables, extensions)
    init_db()
    
    # Run seeder with specified JSON file
    seed_database(json_path)