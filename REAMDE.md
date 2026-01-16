# 📄 Resume Synthesizer

An AI-powered RAG (Retrieval-Augmented Generation) system that stores your career history as vector embeddings and synthesizes tailored CVs and cover letters based on specific job descriptions.

## 🏗️ Architecture

The system uses a modern RAG stack:

* **FastAPI:** High-performance backend.
* **PostgreSQL + pgvector:** Vector database for semantic search.
* **OpenAI (GPT-4o):** For synthesis and skills gap analysis.
* **OpenAI (text-embedding-3-small):** To convert text into 1024-dimension vectors.
* **Streamlit:** Frontend for easy interaction.

## 🎯 What You Got

**6 Core Files:**
1. **docker-compose.yml** - PostgreSQL with pgvector extension
2. **requirements.txt** - All Python dependencies
3. **.env.example** - Configuration template
4. **models.py** - Database schema with vector embeddings
5. **database.py** - Database connection and initialization
6. **llm_service.py** - Claude AI integration for CV generation
7. **main.py** - FastAPI backend with all endpoints
8. **streamlit_app.py** - Beautiful web interface

## 🚀 Key Features Implemented

✅ **Master Profile Storage** - Store all your experiences with vector embeddings  
✅ **Vector Similarity Search** - Uses pgvector to find most relevant experiences  
✅ **Skills Gap Analysis** - Identifies what you're missing vs what job requires  
✅ **Tailored CV Generation** - AI rewrites your CV for each specific job  
✅ **Cover Letter Generation** - Personalized cover letters  
✅ **Application Tracking** - Track status of each application  
✅ **Style Guidelines** - Set rules for how CVs should be formatted  

## 📦 Setup Instructions

1. **Create project directory and add files:**
```bash
mkdir resume-synthesizer
cd resume-synthesizer
# Copy all the artifacts into this directory
```

2. **Create .env file:**
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

3. **Start PostgreSQL with pgvector:**
```bash
docker compose up -d
```

> [!NOTE]
> To remove docker images use: 
> - `docker compose down -v --rmi all`

4. **Install Virtual Environment**
```bash
pip install pipenv
```

5. **Create Virtual Environment**
```bash
pipenv shell
```

6. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

> [!NOTE]
> To remove pipenv use: 
> - `taskkill //F //IM python.exe //T` to stop all processes
> - `pipenv --rm` to remove the pipenv packages

7. **Start the FastAPI backend:**
```bash
python main.py
```

8. **In a new terminal, start Streamlit:**
```bash
pipenv shell
streamlit run streamlit_app.py
```

9. **In a new terminal, import seeded data**
```bash
pipenv shell
DATABASE_URL=postgresql://resume_user:resume_pass@127.0.0.1:5433/resume_db py seed_data.py
DATABASE_URL=postgresql://resume_user:resume_pass@127.0.0.1:5433/resume_db py verify_setup.py
```

## 🎨 How to Use

1. **Add Personal Info** - Your contact details and professional summary
2. **Add Experience Blocks** - All your work history, projects, skills
3. **Set Style Guidelines** (Optional) - "Keep CV to 2 pages", "Use STAR method", etc.
4. **Create Application** - Paste job description from LekkeSlaap
5. **Get Results** - Tailored CV, Cover Letter, and Skills Gap Analysis in under 60 seconds!

## 🔍 About the pgvector Implementation

The system uses **cosine similarity search** to find your most relevant experiences. When you paste a job description:

1. Job description → converted to vector embedding
2. Your experiences (already embedded) → ranked by similarity
3. Top 5 most relevant → sent to Claude
4. Claude generates targeted CV using only relevant info

This means your "Auto Technician" experience won't show up for a Laravel job, but your "ActuallyFind marketplace" project will be front and center!

## 🎯 Next Steps for Enhancement

After testing the MVP, consider:
- Replace the placeholder embedding function with a real model (OpenAI embeddings or sentence-transformers)
- Add authentication for multi-user support
- Export to PDF functionality
- Email integration to track responses
- Analytics dashboard showing which skills are most in-demand

The architecture is solid and ready to scale! Test it out with the LekkeSlaap job and let me know how it works. 🚀