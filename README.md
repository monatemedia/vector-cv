# 📄 Vector CV: Resume Synthesizer

An advanced AI-powered **RAG (Retrieval-Augmented Generation)** system that transforms your career history into semantic vector embeddings. It intelligently synthesizes tailored CVs and cover letters by matching your professional DNA to specific job descriptions.

## 🏗️ System Architecture

Vector CV follows a modern, containerized microservices architecture:

* **FastAPI Backend:** High-performance Python core handling business logic and LLM orchestration.
* **PostgreSQL + pgvector:** Vector database performing high-speed **Cosine Similarity** searches.
* **OpenAI GPT-4o:** Advanced synthesis engine for CV generation and skills gap analysis.
* **OpenAI text-embedding-3-small:** Truncated to **1024-dimensional vectors** for an optimal balance of semantic accuracy and retrieval performance.
* **React + Vite:** Responsive SPA (Single Page Application) for the end-user interface.
* **Streamlit:** Internal administrative panel for master data management and system monitoring.
* **Nginx Reverse Proxy:** Unified entry point handling SSL, WebSocket streams, and path-based routing.

## 🚀 Key Features

* ✅ **Semantic Master Profile** – Store your work history as high-dimensional vectors.
* ✅ **Hybrid Retrieval** – Combines vector similarity, keyword matching, and project priority logic.
* ✅ **Dynamic CV Synthesis** – Generates resumes in your exact voice using few-shot prompting.
* ✅ **Skills Gap Analysis** – Identifies missing requirements to help you prepare for interviews.
* ✅ **Administrative Panel** – Full CRUD interface for experience blocks and style guidelines.
* ✅ **Production Ready** – Multi-stage Docker builds with an automated Nginx orchestration.

## 🛠️ Technical Implementation

### The Vector Engine

The system utilizes **Cosine Distance** calculations () to rank experience blocks.

* **Embedding Model:** `text-embedding-3-small`
* **Dimensions:** 1024 (Truncated for performance)
* **Vector Ops:** Performed natively in SQL via `pgvector`.

### DevOps & Orchestration

The deployment is managed via a **Multi-stage Dockerfile**, separating the Node.js build environment from the Python production runtime to minimize image size and security surface area.

## 📦 Rapid Deployment (Docker)

1. **Clone the Repository:**
```bash
git clone https://github.com/monatemedia/vector-cv.git
cd vector-cv

```


2. **Configure Environment:**
```bash
cp .env.example .env
# Add your OPENAI_API_KEY and Database credentials

```


3. **Launch the Stack:**
```bash
# Deploy script
./deploy.sh

```


*The system will be available at `http://localhost` (or your configured VIRTUAL_HOST).*

## 🎨 Workflow

1. **Seed Data:** Input your contact details and professional summary.
2. **Vectorize Experience:** Add work history blocks; the system automatically generates embeddings on save.
3. **Define Style:** Set specific guardrails (e.g., "Must follow STAR method," "Limit to 2 pages").
4. **Synthesize:** Paste a job description. The RAG engine retrieves the most relevant 1024d vectors and prompts GPT-4o to generate your tailored application materials.