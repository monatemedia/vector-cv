from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import uuid
import os
from collections import defaultdict
from database import get_db, init_db
from models import (
    ExperienceBlock, PersonalInfo, StyleGuideline,
    JobApplication, ApplicationStatus, BlockType
)
from llm_service import (
    generate_embedding, analyze_skills_gap,
    generate_tailored_cv, generate_cover_letter,
    extract_skills_from_job
)
from docx_generator import generate_cv_docx, generate_cover_letter_docx

app = FastAPI(title="Resume Synthesizer API")

# Create output directory for Word docs
OUTPUT_DIR = "./generated_docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8501",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8501",
        # Add your production domains here
        "https://cv.yourdomain.com",
        "https://vectorcv.yourdomain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple rate limiting
usage_tracker = defaultdict(list)
MAX_REQUESTS_PER_DAY = int(os.getenv("MAX_CV_PER_DAY", "3"))

def check_rate_limit(client_ip: str):
    """Check if client has exceeded daily rate limit"""
    now = datetime.now()
    
    # Clean old entries
    usage_tracker[client_ip] = [
        timestamp for timestamp in usage_tracker[client_ip]
        if now - timestamp < timedelta(days=1)
    ]
    
    # Check limit
    if len(usage_tracker[client_ip]) >= MAX_REQUESTS_PER_DAY:
        raise HTTPException(
            status_code=429,
            detail=f"Daily limit of {MAX_REQUESTS_PER_DAY} CV generations reached. Please try again tomorrow."
        )
    
    # Log this request
    usage_tracker[client_ip].append(now)

# --- Pydantic Models ---

class ExperienceBlockCreate(BaseModel):
    title: str
    company: Optional[str] = None
    content: str
    metadata_tags: List[str] = []
    block_type: Optional[str] = "supporting_project"
    priority: Optional[str] = "3"

class ExperienceBlockResponse(BaseModel):
    id: uuid.UUID
    title: str
    company: Optional[str] = None
    content: str
    metadata_tags: Optional[List[str]] = []
    block_type: Optional[str] = None
    priority: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

class PersonalInfoCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    summary: Optional[str] = None

class PersonalInfoResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    linkedin: Optional[str]
    github: Optional[str]
    portfolio: Optional[str]
    summary: Optional[str]
    class Config:
        from_attributes = True

class StyleGuidelineCreate(BaseModel):
    name: str
    description: Optional[str] = None
    rules: Dict = {}
    is_active: str = "true"

class JobApplicationCreate(BaseModel):
    company_name: str
    job_title: str
    raw_spec: str
    job_url: Optional[str] = None

class JobApplicationResponse(BaseModel):
    id: uuid.UUID
    company_name: str
    job_title: str
    generated_cv: Optional[str]
    generated_cover_letter: Optional[str]
    skills_gap_report: Optional[Dict]
    status: ApplicationStatus
    created_at: datetime
    cv_docx_path: Optional[str] = None
    cover_letter_docx_path: Optional[str] = None
    class Config:
        from_attributes = True

class StyleGuidelineResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    rules: Optional[Dict] = {}
    is_active: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Helper Functions ---

def select_relevant_blocks(job_description: str, db: Session) -> List[ExperienceBlock]:
    """Hybrid selection strategy for experience blocks"""
    
    job_embedding = generate_embedding(job_description)
    job_skills = extract_skills_from_job(job_description)
    print(f"📊 Extracted {len(job_skills)} skills from job: {job_skills[:10]}")
    
    selected_blocks = []
    selected_ids = set()
    
    # 1. ALWAYS include pillar projects
    pillar_blocks = db.query(ExperienceBlock).filter(
        ExperienceBlock.block_type == BlockType.PILLAR_PROJECT
    ).all()
    
    for block in pillar_blocks:
        selected_blocks.append(block)
        selected_ids.add(block.id)
    print(f"✅ Added {len(pillar_blocks)} pillar projects")
    
    # 2. ALWAYS include skills summary
    skills_summary = db.query(ExperienceBlock).filter(
        ExperienceBlock.block_type == BlockType.SKILLS_SUMMARY
    ).first()
    
    if skills_summary:
        selected_blocks.append(skills_summary)
        selected_ids.add(skills_summary.id)
        print(f"✅ Added skills summary")
    
    # 3. Find blocks matching required skills
    skill_matched_blocks = []
    for skill in job_skills:
        matching_blocks = db.query(ExperienceBlock).filter(
            ExperienceBlock.id.notin_(selected_ids),
            ExperienceBlock.block_type.in_([BlockType.SUPPORTING_PROJECT, BlockType.PILLAR_PROJECT])
        ).all()
        
        for block in matching_blocks:
            if block.metadata_tags and any(
                skill.lower() in tag.lower() for tag in block.metadata_tags
            ):
                if block.id not in selected_ids:
                    skill_matched_blocks.append(block)
                    selected_ids.add(block.id)
                    break
    
    selected_blocks.extend(skill_matched_blocks)
    print(f"✅ Added {len(skill_matched_blocks)} skill-matched projects")
    
    # 4. Vector search for additional projects
    vector_blocks = db.query(ExperienceBlock).filter(
        ExperienceBlock.id.notin_(selected_ids),
        ExperienceBlock.block_type == BlockType.SUPPORTING_PROJECT
    ).order_by(
        ExperienceBlock.embedding.cosine_distance(job_embedding)
    ).limit(3).all()
    
    selected_blocks.extend(vector_blocks)
    for block in vector_blocks:
        selected_ids.add(block.id)
    print(f"✅ Added {len(vector_blocks)} vector-matched projects")
    
    # 5. Add most recent employment
    employment = db.query(ExperienceBlock).filter(
        ExperienceBlock.block_type == BlockType.EMPLOYMENT
    ).order_by(desc(ExperienceBlock.created_at)).first()
    
    if employment and employment.id not in selected_ids:
        selected_blocks.append(employment)
        selected_ids.add(employment.id)
        print(f"✅ Added employment history")
    
    # 6. Add education
    education = db.query(ExperienceBlock).filter(
        ExperienceBlock.block_type == BlockType.EDUCATION
    ).first()
    
    if education and education.id not in selected_ids:
        selected_blocks.append(education)
        print(f"✅ Added education")
    
    print(f"📦 Total blocks selected: {len(selected_blocks)}")
    return selected_blocks

# --- Lifecycle ---

@app.on_event("startup")
def startup_event():
    init_db()

# --- Endpoints ---

@app.get("/")
def read_root():
    return {
        "message": "Resume Synthesizer API",
        "docs": "/docs",
        "status": "running",
        "version": "2.0",
        "features": ["Vector RAG", "Hybrid Selection", "AI-Powered Generation", "Word Document Export"]
    }

# Personal Info
@app.post("/api/personal-info", response_model=PersonalInfoResponse)
def create_personal_info(info: PersonalInfoCreate, db: Session = Depends(get_db)):
    existing = db.query(PersonalInfo).first()
    if existing:
        for key, value in info.dict().items():
            setattr(existing, key, value)
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing
    db_info = PersonalInfo(**info.dict())
    db.add(db_info)
    db.commit()
    db.refresh(db_info)
    return db_info

@app.get("/api/personal-info", response_model=PersonalInfoResponse)
def get_personal_info(db: Session = Depends(get_db)):
    info = db.query(PersonalInfo).first()
    if not info:
        raise HTTPException(status_code=404, detail="Personal info not found")
    return info

# Experience Blocks
@app.post("/api/experience-blocks", response_model=ExperienceBlockResponse)
def create_experience_block(exp: ExperienceBlockCreate, db: Session = Depends(get_db)):
    embedding = generate_embedding(exp.content)
    block_type_enum = BlockType(exp.block_type) if exp.block_type else BlockType.SUPPORTING_PROJECT
    
    db_exp = ExperienceBlock(
        title=exp.title,
        company=exp.company,
        content=exp.content,
        metadata_tags=exp.metadata_tags,
        block_type=block_type_enum,
        priority=exp.priority,
        embedding=embedding
    )
    db.add(db_exp)
    db.commit()
    db.refresh(db_exp)
    return db_exp

@app.get("/api/experience-blocks", response_model=List[ExperienceBlockResponse])
def list_experience_blocks(db: Session = Depends(get_db)):
    return db.query(ExperienceBlock).order_by(desc(ExperienceBlock.created_at)).all()

@app.delete("/api/experience-blocks/{block_id}")
def delete_experience_block(block_id: uuid.UUID, db: Session = Depends(get_db)):
    block = db.query(ExperienceBlock).filter(ExperienceBlock.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Experience block not found")
    db.delete(block)
    db.commit()
    return {"message": "Deleted successfully"}

# Applications
@app.post("/api/applications", response_model=JobApplicationResponse)
def create_job_application(
    app_data: JobApplicationCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    # Rate limiting
    if os.getenv("ENABLE_RATE_LIMITING", "false").lower() == "true":
        client_ip = request.client.host
        check_rate_limit(client_ip)
        print(f"🔒 Rate limit check passed for {client_ip}")
    
    personal_info = db.query(PersonalInfo).first()
    if not personal_info:
        raise HTTPException(status_code=400, detail="Please add your personal info first")
    
    # Use hybrid selection strategy
    print(f"\n🔍 Analyzing job: {app_data.job_title} at {app_data.company_name}")
    experiences = select_relevant_blocks(app_data.raw_spec, db)
    
    if not experiences:
        raise HTTPException(status_code=400, detail="Please add at least one experience block first")
    
    experience_chunks = [
        {
            "title": exp.title,
            "company": exp.company,
            "content": exp.content,
            "metadata_tags": exp.metadata_tags or []
        }
        for exp in experiences
    ]
    
    personal_dict = {
        "name": personal_info.name,
        "email": personal_info.email,
        "phone": personal_info.phone,
        "location": personal_info.location,
        "linkedin": personal_info.linkedin,
        "github": personal_info.github,
        "portfolio": personal_info.portfolio,
        "summary": personal_info.summary
    }
    
    style_guidelines = db.query(StyleGuideline).filter(StyleGuideline.is_active == "true").all()
    style_dicts = [{"name": sg.name, "description": sg.description} for sg in style_guidelines]
    
    print(f"📝 Generating CV with {len(experience_chunks)} blocks...")
    skills_gap = analyze_skills_gap(experience_chunks, app_data.raw_spec)
    cv = generate_tailored_cv(personal_dict, experience_chunks, app_data.raw_spec, style_dicts)
    cover_letter = generate_cover_letter(
        personal_dict, experience_chunks, app_data.raw_spec,
        app_data.company_name, app_data.job_title
    )
    
    # Generate Word documents
    print(f"📄 Generating Word documents...")
    try:
        cv_docx_path = generate_cv_docx(cv, app_data.company_name, app_data.job_title, OUTPUT_DIR)
        cover_docx_path = generate_cover_letter_docx(cover_letter, app_data.company_name, app_data.job_title, OUTPUT_DIR)
        print(f"✅ Word documents generated")
    except Exception as e:
        print(f"⚠️  Word document generation failed: {e}")
        cv_docx_path = None
        cover_docx_path = None
    
    db_app = JobApplication(
        company_name=app_data.company_name,
        job_title=app_data.job_title,
        raw_spec=app_data.raw_spec,
        job_url=app_data.job_url,
        generated_cv=cv,
        generated_cover_letter=cover_letter,
        skills_gap_report=skills_gap,
        status=ApplicationStatus.DRAFT
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    
    # Add docx paths to response
    response = JobApplicationResponse.from_orm(db_app)
    response.cv_docx_path = cv_docx_path
    response.cover_letter_docx_path = cover_docx_path
    
    print(f"✅ Application created successfully\n")
    return response

@app.get("/api/applications", response_model=List[JobApplicationResponse])
def list_applications(db: Session = Depends(get_db)):
    return db.query(JobApplication).order_by(desc(JobApplication.created_at)).all()

# Download endpoints for Word documents
@app.get("/api/download/cv/{application_id}")
def download_cv(application_id: uuid.UUID, db: Session = Depends(get_db)):
    """Download CV as Word document"""
    app = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Generate fresh Word doc
    try:
        cv_path = generate_cv_docx(app.generated_cv, app.company_name, app.job_title, OUTPUT_DIR)
        return FileResponse(
            cv_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"CV_{app.company_name}_{app.job_title}.docx"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Word document: {str(e)}")

@app.get("/api/download/cover-letter/{application_id}")
def download_cover_letter(application_id: uuid.UUID, db: Session = Depends(get_db)):
    """Download cover letter as Word document"""
    app = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Generate fresh Word doc
    try:
        cover_path = generate_cover_letter_docx(app.generated_cover_letter, app.company_name, app.job_title, OUTPUT_DIR)
        return FileResponse(
            cover_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"CoverLetter_{app.company_name}_{app.job_title}.docx"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Word document: {str(e)}")

# Style Guidelines
@app.post("/api/style-guidelines", response_model=StyleGuidelineResponse)
def create_style_guideline(guideline: StyleGuidelineCreate, db: Session = Depends(get_db)):
    db_guideline = StyleGuideline(**guideline.dict())
    db.add(db_guideline)
    db.commit()
    db.refresh(db_guideline)
    return db_guideline

@app.get("/api/style-guidelines", response_model=List[StyleGuidelineResponse])
def list_style_guidelines(db: Session = Depends(get_db)):
    return db.query(StyleGuideline).filter(StyleGuideline.is_active == "true").all()

# --- Runtime ---

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)