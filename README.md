# 📄 Vector CV: Resume Synthesizer

An AI-powered RAG (Retrieval-Augmented Generation) system that stores your career history as vector embeddings and synthesizes tailored CVs and cover letters based on specific job descriptions.

## 🏗️ Architecture

The system uses a modern RAG stack:

* **FastAPI:** High-performance backend.
* **PostgreSQL + pgvector:** Vector database for semantic search.
* **OpenAI (GPT-4o):** For synthesis and skills gap analysis.
* **OpenAI (text-embedding-3-small):** To convert text into 1024-dimension vectors.
* **Streamlit:** Admin frontend for easy interaction.
* **React:** User frontend for user interaction.

## 🎯 What You Got

**6 Core Files:**
1. **docker-compose.yml** - PostgreSQL with pgvector extension
2. **requirements.txt** - All Python dependencies
3. **.env.example** - Configuration template
4. **models.py** - Database schema with vector embeddings
5. **database.py** - Database connection and initialization
6. **llm_service.py** - Claude AI integration for CV generation
7. **main.py** - FastAPI backend with all endpoints
8. **streamlit_app.py** - Beautiful admin web interface
9. **App.jsx** - Beautiful user web interface

## 🚀 Key Features Implemented

✅ **Master Profile Storage** - Store all your experiences with vector embeddings  
✅ **Vector Similarity Search** - Uses pgvector to find most relevant experiences  
✅ **Skills Gap Analysis** - Identifies what you're missing vs what job requires  
✅ **Tailored CV Generation** - AI rewrites your CV for each specific job  
✅ **Cover Letter Generation** - Personalized cover letters  
✅ **Application Tracking** - Track status of each application  
✅ **Style Guidelines** - Set rules for how CVs should be formatted  

## 📦 Setup Instructions

1. **Copy the files to your local machine**
```bash
git clone https://github.com/monatemedia/vector-cv.git
```

2. **Change directory into project folder:**
```bash
cd vector-cv
```

1. **Create .env file:**
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

1. **Start PostgreSQL with pgvector:**
```bash
# Check if Docker is running
docker compose up -d
```

> [!NOTE]
> To remove docker images use: 
> - `docker compose down -v --rmi all`
> To remove all stale docker images use (with caution)
> - `docker system prune -f`

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
pipenv install -r requirements.txt
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
export $(grep -v '^#' .env | xargs) && python seed_data.py
export $(grep -v '^#' .env | xargs) && python verify_setup.py
```

10. **In a new terminal, start the frontend**
```sh
npm run dev --prefix frontend
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