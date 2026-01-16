from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import uuid
from database import get_db, init_db
from models import (
    ExperienceBlock, PersonalInfo, StyleGuideline, 
    JobApplication, ApplicationStatus
)
from llm_service import (
    generate_embedding, analyze_skills_gap,
    generate_tailored_cv, generate_cover_letter
)

app = FastAPI(title="Resume Synthesizer API")

# --- Pydantic Models ---

class ExperienceBlockCreate(BaseModel):
    title: str
    company: Optional[str] = None
    content: str
    metadata_tags: List[str] = []

class ExperienceBlockResponse(BaseModel):
    id: uuid.UUID
    title: str
    company: Optional[str] = None
    content: str
    metadata_tags: Optional[List[str]] = []
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

# --- Lifecycle ---

@app.on_event("startup")
def startup_event():
    init_db()

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Resume Synthesizer API", "docs": "/docs", "status": "running"}

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
    db_exp = ExperienceBlock(**exp.dict(), embedding=embedding)
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
def create_job_application(app_data: JobApplicationCreate, db: Session = Depends(get_db)):
    personal_info = db.query(PersonalInfo).first()
    if not personal_info:
        raise HTTPException(status_code=400, detail="Please add your personal info first")
    
    job_embedding = generate_embedding(app_data.raw_spec)
    
    # Vector Similarity Search
    experiences = db.query(ExperienceBlock).order_by(
        ExperienceBlock.embedding.cosine_distance(job_embedding)
    ).limit(5).all()
    
    if not experiences:
        raise HTTPException(status_code=400, detail="Please add at least one experience block first")

    experience_chunks = [
        {"title": exp.title, "company": exp.company, "content": exp.content, "metadata_tags": exp.metadata_tags or []}
        for exp in experiences
    ]
    
    personal_dict = {
        "name": personal_info.name, "email": personal_info.email, "phone": personal_info.phone,
        "location": personal_info.location, "linkedin": personal_info.linkedin,
        "github": personal_info.github, "summary": personal_info.summary
    }

    style_guidelines = db.query(StyleGuideline).filter(StyleGuideline.is_active == "true").all()
    style_dicts = [{"name": sg.name, "description": sg.description} for sg in style_guidelines]

    skills_gap = analyze_skills_gap(experience_chunks, app_data.raw_spec)
    cv = generate_tailored_cv(personal_dict, experience_chunks, app_data.raw_spec, style_dicts)
    cover_letter = generate_cover_letter(personal_dict, experience_chunks, app_data.raw_spec, app_data.company_name, app_data.job_title)

    db_app = JobApplication(
        company_name=app_data.company_name, job_title=app_data.job_title,
        raw_spec=app_data.raw_spec, job_url=app_data.job_url,
        generated_cv=cv, generated_cover_letter=cover_letter,
        skills_gap_report=skills_gap, status=ApplicationStatus.DRAFT
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

@app.get("/api/applications", response_model=List[JobApplicationResponse])
def list_applications(db: Session = Depends(get_db)):
    return db.query(JobApplication).order_by(desc(JobApplication.created_at)).all()

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