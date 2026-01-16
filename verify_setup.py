"""
Verification script to check if your Vector CV database is properly configured
Run this after migration or fresh seed to ensure everything is working
"""

from sqlalchemy import create_engine, text
from database import SessionLocal
from models import ExperienceBlock, PersonalInfo, BlockType
import os
from dotenv import load_dotenv

load_dotenv()

def verify_setup():
    print("=" * 60)
    print("VECTOR CV DATABASE VERIFICATION")
    print("=" * 60)
    
    db = SessionLocal()
    
    # 1. Check personal info
    print("\n1. Personal Information:")
    personal = db.query(PersonalInfo).first()
    if personal:
        print(f"   ✅ Name: {personal.name}")
        print(f"   ✅ Email: {personal.email}")
        print(f"   ✅ Portfolio: {personal.portfolio}")
    else:
        print("   ❌ No personal info found - run seed_data.py")
        return
    
    # 2. Check block counts by type
    print("\n2. Experience Blocks by Type:")
    
    block_counts = {}
    for block_type in BlockType:
        count = db.query(ExperienceBlock).filter(
            ExperienceBlock.block_type == block_type
        ).count()
        block_counts[block_type.value] = count
        
        status = "✅" if count > 0 else "⚠️"
        print(f"   {status} {block_type.value}: {count}")
    
    # 3. Verify critical blocks
    print("\n3. Critical Blocks Check:")
    
    critical_checks = [
        ("Skills Summary", BlockType.SKILLS_SUMMARY, 1),
        ("Pillar Projects", BlockType.PILLAR_PROJECT, 2),
        ("Employment", BlockType.EMPLOYMENT, 1),
        ("Education", BlockType.EDUCATION, 1)
    ]
    
    all_critical_present = True
    for name, block_type, expected_min in critical_checks:
        count = block_counts.get(block_type.value, 0)
        if count >= expected_min:
            print(f"   ✅ {name}: {count} (need ≥{expected_min})")
        else:
            print(f"   ❌ {name}: {count} (need ≥{expected_min})")
            all_critical_present = False
    
    # 4. Check for required skills in skills summary
    print("\n4. Skills Coverage:")
    
    skills_summary = db.query(ExperienceBlock).filter(
        ExperienceBlock.block_type == BlockType.SKILLS_SUMMARY
    ).first()
    
    if skills_summary:
        required_skills = ["Laravel", "React", "Docker", "PostgreSQL", "Python"]
        missing_skills = []
        
        for skill in required_skills:
            if skill in skills_summary.content or (
                skills_summary.metadata_tags and skill in skills_summary.metadata_tags
            ):
                print(f"   ✅ {skill}")
            else:
                print(f"   ❌ {skill} - not found in skills summary")
                missing_skills.append(skill)
        
        if missing_skills:
            print(f"\n   ⚠️  Missing skills: {', '.join(missing_skills)}")
            print("   Consider updating your skills summary block")
    else:
        print("   ❌ No skills summary block found!")
    
    # 5. Check embeddings
    print("\n5. Embeddings Status:")
    
    total_blocks = db.query(ExperienceBlock).count()
    blocks_with_embeddings = db.query(ExperienceBlock).filter(
        ExperienceBlock.embedding.isnot(None)
    ).count()
    
    if blocks_with_embeddings == total_blocks:
        print(f"   ✅ All {total_blocks} blocks have embeddings")
    else:
        print(f"   ⚠️  Only {blocks_with_embeddings}/{total_blocks} blocks have embeddings")
        print("   Run seed_data.py to regenerate embeddings")
    
    # 6. List all blocks
    print("\n6. All Experience Blocks:")
    
    all_blocks = db.query(ExperienceBlock).order_by(
        ExperienceBlock.block_type, 
        ExperienceBlock.priority
    ).all()
    
    current_type = None
    for block in all_blocks:
        if block.block_type != current_type:
            current_type = block.block_type
            print(f"\n   {current_type.value.upper().replace('_', ' ')}:")
        
        priority_indicator = "⭐" * int(block.priority or "3")
        print(f"   {priority_indicator} {block.title}")
        if block.metadata_tags:
            tag_count = len(block.metadata_tags)
            sample_tags = ", ".join(block.metadata_tags[:5])
            print(f"      └─ {tag_count} skills: {sample_tags}...")
    
    # 7. Final recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS:")
    print("=" * 60)
    
    if not all_critical_present:
        print("❌ Missing critical blocks - run seed_data.py to fix")
    elif blocks_with_embeddings < total_blocks:
        print("⚠️  Missing embeddings - regenerate with seed_data.py")
    else:
        print("✅ Database looks healthy!")
        print("\nNext steps:")
        print("1. Test application generation with LekkeSlaap job")
        print("2. Verify React and all skills appear in CV")
        print("3. Compare output to your manual CV")
    
    db.close()

def test_skill_extraction():
    """Test the skill extraction function"""
    print("\n" + "=" * 60)
    print("TESTING SKILL EXTRACTION")
    print("=" * 60)
    
    from llm_service import extract_skills_from_job
    
    sample_job = """
    We're looking for a Full Stack Developer with experience in:
    - Laravel and PHP
    - React or Vue.js
    - PostgreSQL or MySQL
    - Docker and CI/CD
    - AWS cloud experience
    """
    
    print("\nSample Job Description:")
    print(sample_job)
    
    print("\nExtracting skills...")
    skills = extract_skills_from_job(sample_job)
    
    if skills:
        print(f"\n✅ Extracted {len(skills)} skills:")
        for skill in skills:
            print(f"   - {skill}")
    else:
        print("\n❌ Skill extraction failed - check OpenAI API key")

if __name__ == "__main__":
    try:
        verify_setup()
        
        # Uncomment to test skill extraction
        # test_skill_extraction()
        
    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        print("\nTroubleshooting:")
        print("1. Check DATABASE_URL in .env file")
        print("2. Ensure PostgreSQL is running")
        print("3. Run: python database.py to initialize database")
        print("4. Run: python seed_data.py to populate data")