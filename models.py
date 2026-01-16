from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector
import uuid
import enum

Base = declarative_base()

class ApplicationStatus(str, enum.Enum):
    DRAFT = "draft"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    REJECTED = "rejected"
    OFFER = "offer"
    ACCEPTED = "accepted"

class BlockType(str, enum.Enum):
    PILLAR_PROJECT = "pillar_project"      # ActuallyFind, Vector CV
    SUPPORTING_PROJECT = "supporting_project"  # Other projects
    EMPLOYMENT = "employment"              # Job roles
    EDUCATION = "education"                # Education block
    SKILLS_SUMMARY = "skills_summary"      # Comprehensive skills list

class ExperienceBlock(Base):
    __tablename__ = "experience_blocks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    company = Column(String(200))
    content = Column(Text, nullable=False)
    metadata_tags = Column(JSON)  # Store skills/keywords as JSON array
    block_type = Column(SQLEnum(BlockType), default=BlockType.SUPPORTING_PROJECT)  # NEW FIELD
    priority = Column(String(10), default="3")  # 1=highest, 5=lowest (for ordering within type)
    embedding = Column(Vector(1024))  # OpenAI's embedding dimension
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PersonalInfo(Base):
    __tablename__ = "personal_info"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    email = Column(String(200))
    phone = Column(String(50))
    location = Column(String(200))
    linkedin = Column(String(500))
    github = Column(String(500))
    portfolio = Column(String(500))
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StyleGuideline(Base):
    __tablename__ = "style_guidelines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    rules = Column(JSON)  # Store rules as structured JSON
    is_active = Column(String(10), default="true")
    created_at = Column(DateTime, default=datetime.utcnow)

class JobApplication(Base):
    __tablename__ = "job_applications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(200), nullable=False)
    job_title = Column(String(200), nullable=False)
    raw_spec = Column(Text, nullable=False)
    generated_cv = Column(Text)
    generated_cover_letter = Column(Text)
    skills_gap_report = Column(JSON)
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.DRAFT)
    applied_date = Column(DateTime)
    notes = Column(Text)
    job_url = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)