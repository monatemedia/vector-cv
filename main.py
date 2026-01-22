from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import uuid
import os
import json
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

# --- Security Configuration ---
security = HTTPBearer()
ADMIN_KEY = os.getenv("ADMIN_API_KEY", "dev_secret")

def verify_admin_key(auth: HTTPAuthorizationCredentials = Depends(security)):
    """Authorize destructive or administrative actions"""
    if auth.credentials != ADMIN_KEY:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized: Administrative access required."
        )

# Separate trackers for different tiers
browse_tracker = defaultdict(list)  # For GET requests
ai_tracker = defaultdict(list)      # For POST /api/applications

def check_general_rate_limit(request: Request):
    """60 requests per hour for browsing"""
    if os.getenv("ENABLE_RATE_LIMITING", "false").lower() != "true":
        return

    # Standardize IP extraction
    forwarded = request.headers.get("X-Forwarded-For")
    client_ip = forwarded.split(",")[0] if forwarded else request.client.host
    now = datetime.now()

    # 1. Clean and check (1 hour window)
    browse_tracker[client_ip] = [t for t in browse_tracker[client_ip] if now - t < timedelta(hours=1)]

    # 2. Check limit
    limit = int(os.getenv("GENERAL_RATE_LIMIT", "60"))
    if len(browse_tracker[client_ip]) >= limit:
        print(f"⚠️ General Rate Limit hit: {client_ip}")
        raise HTTPException(
            status_code=429,
            detail=f"Browsing limit of {limit} requests per hour reached."
        )

    # 3. Log
    browse_tracker[client_ip].append(now)

def check_ai_usage_allowed(request: Request):
    """Checks if the user has attempts left without consuming one"""
    if os.getenv("ENABLE_RATE_LIMITING", "false").lower() != "true":
        return

    forwarded = request.headers.get("X-Forwarded-For")
    client_ip = forwarded.split(",")[0] if forwarded else request.client.host
    now = datetime.now()

    # Clean old entries
    ai_tracker[client_ip] = [t for t in ai_tracker[client_ip] if now - t < timedelta(days=1)]

    if len(ai_tracker[client_ip]) >= int(os.getenv("MAX_CV_PER_DAY", "3")):
        raise HTTPException(status_code=429, detail="Daily AI generation limit reached.")

def log_ai_usage_success(request: Request):
    """Call this ONLY after a successful AI generation"""
    if os.getenv("ENABLE_RATE_LIMITING", "false").lower() != "true":
        return

    forwarded = request.headers.get("X-Forwarded-For")
    client_ip = forwarded.split(",")[0] if forwarded else request.client.host
    ai_tracker[client_ip].append(datetime.now())

# Create the app with a dynamic root_path
app = FastAPI(
    title="Vector CV API",
    # This allows Swagger to work behind the Nginx /api prefix
    root_path=os.getenv("PROXY_ROOT_PATH", "")
)

# Create output directory for Word docs
OUTPUT_DIR = "./generated_docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# CORS Configuration
raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
origins = [origin.strip() for origin in raw_origins]
# Add common dev ports just in case
if "http://localhost:3000" not in origins: origins.append("http://localhost:3000")
if "http://localhost:5173" not in origins: origins.append("http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---

class ExperienceBlockCreate(BaseModel):
    title: str
    company: Optional[str] = None
    content: str
    metadata_tags: List[str] = []
    block_type: Optional[str] = "supporting_project"
    priority: Optional[str] = "3"

class ExperienceBlockUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    content: Optional[str] = None
    metadata_tags: Optional[List[str]] = None
    block_type: Optional[str] = None
    priority: Optional[str] = None

class ExperienceBlockResponse(BaseModel):
    id: uuid.UUID
    title: str
    company: Optional[str] = None
    content: str
    metadata_tags: Optional[List[str]] = []
    block_type: Optional[str] = None
    priority: Optional[str] = None
    created_at: datetime
    updated_at: datetime
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

class JobApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    applied_date: Optional[datetime] = None

class JobApplicationResponse(BaseModel):
    id: uuid.UUID
    company_name: str
    job_title: str
    generated_cv: Optional[str]
    generated_cover_letter: Optional[str]
    skills_gap_report: Optional[Dict]
    status: ApplicationStatus
    notes: Optional[str]
    applied_date: Optional[datetime]
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

class DataExportResponse(BaseModel):
    personal_info: Dict
    experience_blocks: List[Dict]

class DataImportRequest(BaseModel):
    personal_info: Dict
    experience_blocks: List[Dict]

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

@app.get("/", dependencies=[Depends(check_general_rate_limit)])
def read_root():
    return {
        "message": "Resume Synthesizer API",
        "docs": "/docs",
        "status": "running",
        "version": "2.0",
        "features": ["Vector RAG", "Hybrid Selection", "AI-Powered Generation", "Word Document Export", "Backup/Restore"]
    }

# Personal Info
@app.post("/api/personal-info",
        response_model=PersonalInfoResponse,
        dependencies=[Depends(verify_admin_key)])
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

@app.get("/api/personal-info",
        response_model=PersonalInfoResponse,
        dependencies=[Depends(check_general_rate_limit)])
def get_personal_info(db: Session = Depends(get_db)):
    info = db.query(PersonalInfo).first()
    if not info:
        raise HTTPException(status_code=404, detail="Personal info not found")
    return info

# Experience Blocks
@app.post("/api/experience-blocks", response_model=ExperienceBlockResponse,
          dependencies=[Depends(verify_admin_key)])
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

@app.put("/api/experience-blocks/{block_id}", response_model=ExperienceBlockResponse,
         dependencies=[Depends(verify_admin_key)])
def update_experience_block(
    block_id: uuid.UUID,
    exp: ExperienceBlockUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing experience block"""
    block = db.query(ExperienceBlock).filter(ExperienceBlock.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Experience block not found")
    
    # Update fields that are provided
    update_data = exp.dict(exclude_unset=True)
    
    # Regenerate embedding if content changed
    regenerate_embedding = False
    for key, value in update_data.items():
        if key == "block_type" and value:
            setattr(block, key, BlockType(value))
        else:
            setattr(block, key, value)
        
        if key == "content":
            regenerate_embedding = True
    
    if regenerate_embedding:
        combined_text = f"{block.title} at {block.company}: {block.content} Keywords: {', '.join(block.metadata_tags or [])}"
        block.embedding = generate_embedding(combined_text)
    
    block.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(block)
    return block

@app.get("/api/experience-blocks",
        response_model=List[ExperienceBlockResponse],
        dependencies=[Depends(check_general_rate_limit)])
def list_experience_blocks(
    block_type: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List experience blocks with optional filtering"""
    query = db.query(ExperienceBlock)
    
    # Apply filters
    if block_type:
        try:
            query = query.filter(ExperienceBlock.block_type == BlockType(block_type))
        except ValueError:
            pass  # Invalid block type, ignore filter
    
    if priority:
        query = query.filter(ExperienceBlock.priority == priority)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (ExperienceBlock.title.ilike(search_term)) |
            (ExperienceBlock.company.ilike(search_term)) |
            (ExperienceBlock.content.ilike(search_term))
        )
    
    return query.order_by(desc(ExperienceBlock.created_at)).all()

@app.get("/api/experience-blocks/{block_id}",
        response_model=ExperienceBlockResponse,
        dependencies=[Depends(check_general_rate_limit)])
def get_experience_block(block_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get a single experience block by ID"""
    block = db.query(ExperienceBlock).filter(ExperienceBlock.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Experience block not found")
    return block

@app.delete("/api/experience-blocks/{block_id}",
            dependencies=[Depends(verify_admin_key)])
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
    db: Session = Depends(get_db)):

    # 1. Check if allowed (Raises 429 if limit hit)
    check_ai_usage_allowed(request)

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

    try:
        print(f"📝 Generating CV with {len(experience_chunks)} blocks...")
        skills_gap = analyze_skills_gap(experience_chunks, app_data.raw_spec)
        cv = generate_tailored_cv(personal_dict, experience_chunks, app_data.raw_spec, style_dicts)
        cover_letter = generate_cover_letter(
            personal_dict, experience_chunks, app_data.raw_spec,
            app_data.company_name, app_data.job_title
        )

        # 2. SUCCESS! The AI actually worked. Log the usage now.
        log_ai_usage_success(request)

    except Exception as e:
        print(f"❌ AI Generation failed: {e}")
        # We DON'T log usage here, so the user keeps their credit
        raise HTTPException(status_code=500, detail="AI generation failed. Please try again; your daily limit was not affected.")

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

@app.put("/api/applications/{application_id}",
         response_model=JobApplicationResponse,
         dependencies=[Depends(verify_admin_key)])
def update_application(
    application_id: uuid.UUID,
    app_update: JobApplicationUpdate,
    db: Session = Depends(get_db)
):
    """Update application status, notes, or applied date"""
    app = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    update_data = app_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key == "status" and value:
            setattr(app, key, ApplicationStatus(value))
        else:
            setattr(app, key, value)
    
    app.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(app)
    return app

@app.get("/api/applications",
        response_model=List[JobApplicationResponse],
        dependencies=[Depends(check_general_rate_limit)])
def list_applications(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List applications with optional status filter"""
    query = db.query(JobApplication)
    
    if status:
        try:
            query = query.filter(JobApplication.status == ApplicationStatus(status))
        except ValueError:
            pass  # Invalid status, ignore filter
    
    return query.order_by(desc(JobApplication.created_at)).all()

# Download endpoints for Word documents
@app.get("/api/download/cv/{application_id}",
        dependencies=[Depends(check_general_rate_limit)])
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

@app.get("/api/download/cover-letter/{application_id}",
        dependencies=[Depends(check_general_rate_limit)])
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
@app.post("/api/style-guidelines",
          response_model=StyleGuidelineResponse,
          dependencies=[Depends(verify_admin_key)])
def create_style_guideline(guideline: StyleGuidelineCreate, db: Session = Depends(get_db)):
    db_guideline = StyleGuideline(**guideline.dict())
    db.add(db_guideline)
    db.commit()
    db.refresh(db_guideline)
    return db_guideline

@app.get("/api/style-guidelines",
        response_model=List[StyleGuidelineResponse],
        dependencies=[Depends(check_general_rate_limit)])
def list_style_guidelines(db: Session = Depends(get_db)):
    return db.query(StyleGuideline).filter(StyleGuideline.is_active == "true").all()

# Backup/Restore Endpoints
@app.get("/api/export-data",
        response_model=DataExportResponse,
        dependencies=[Depends(check_general_rate_limit)])
def export_all_data(db: Session = Depends(get_db)):
    """Export all personal info and experience blocks as JSON"""
    personal_info = db.query(PersonalInfo).first()
    experience_blocks = db.query(ExperienceBlock).all()
    
    if not personal_info:
        raise HTTPException(status_code=404, detail="No personal info found")
    
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
    
    blocks_list = [
        {
            "title": block.title,
            "company": block.company,
            "content": block.content,
            "tags": block.metadata_tags or [],
            "block_type": block.block_type.value if block.block_type else "supporting_project",
            "priority": block.priority or "3"
        }
        for block in experience_blocks
    ]
    
    return DataExportResponse(
        personal_info=personal_dict,
        experience_blocks=blocks_list
    )

@app.post("/api/import-data",
          dependencies=[Depends(verify_admin_key)])
def import_all_data(data: DataImportRequest, db: Session = Depends(get_db)):
    """Import personal info and experience blocks from JSON"""
    try:
        # Import personal info
        existing_info = db.query(PersonalInfo).first()
        if existing_info:
            for key, value in data.personal_info.items():
                setattr(existing_info, key, value)
            existing_info.updated_at = datetime.utcnow()
        else:
            db_info = PersonalInfo(**data.personal_info)
            db.add(db_info)
        
        # Import experience blocks
        imported_count = 0
        for block_data in data.experience_blocks:
            # Check if block exists by title
            existing_block = db.query(ExperienceBlock).filter(
                ExperienceBlock.title == block_data["title"]
            ).first()
            
            # Prepare embedding
            combined_text = f"{block_data['title']} at {block_data.get('company', '')}: {block_data['content']} Keywords: {', '.join(block_data.get('tags', []))}"
            embedding = generate_embedding(combined_text)
            
            if existing_block:
                # Update existing block
                existing_block.company = block_data.get("company")
                existing_block.content = block_data["content"]
                existing_block.metadata_tags = block_data.get("tags", [])
                existing_block.block_type = BlockType(block_data.get("block_type", "supporting_project"))
                existing_block.priority = block_data.get("priority", "3")
                existing_block.embedding = embedding
                existing_block.updated_at = datetime.utcnow()
            else:
                # Create new block
                new_block = ExperienceBlock(
                    title=block_data["title"],
                    company=block_data.get("company"),
                    content=block_data["content"],
                    metadata_tags=block_data.get("tags", []),
                    block_type=BlockType(block_data.get("block_type", "supporting_project")),
                    priority=block_data.get("priority", "3"),
                    embedding=embedding
                )
                db.add(new_block)
            
            imported_count += 1
        
        db.commit()
        return {
            "message": "Import successful",
            "imported_blocks": imported_count
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

@app.get("/api/usage-stats")
def get_usage_stats(request: Request):
    """Returns remaining AI generations for the current user"""
    forwarded = request.headers.get("X-Forwarded-For")
    client_ip = forwarded.split(",")[0] if forwarded else request.client.host

    now = datetime.now()
    # Sync the tracker (clean old entries)
    ai_tracker[client_ip] = [t for t in ai_tracker[client_ip] if now - t < timedelta(days=1)]

    used = len(ai_tracker[client_ip])
    max_allowed = int(os.getenv("MAX_CV_PER_DAY", "3"))

    return {
        "used": used,
        "remaining": max(0, max_allowed - used),
        "limit": max_allowed
    }

# --- Runtime ---

if __name__ == "__main__":
    import uvicorn