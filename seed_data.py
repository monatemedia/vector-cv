import os
import uuid
from database import SessionLocal, engine
from models import ExperienceBlock, PersonalInfo, Base, BlockType
from llm_service import generate_embedding

def seed_database():
    print("Starting database seeding...")
    db = SessionLocal()
    
    # Add Personal Info
    print("Seeding Personal Info...")
    me = PersonalInfo(
        name="Edward Baitsewe",
        email="edward@monatemedia.com",
        phone="+27 78 324 5326",
        location="Parow, Cape Town",
        linkedin="https://www.linkedin.com/in/edwardbaitsewe",
        github="https://github.com/monatemedia",
        portfolio="https://monatemedia.com/portfolio",
        summary="Full stack developer with 5 years of experience building and deploying scalable webapps. Expert in the **Laravel** ecosystem with a deep focus on search optimization, geospatial data, and CI/CD automation. Proven ability to architect high-availability systems under resource constraints. Former financial advisor with over a decade track record of high-stakes stakeholder management and client service excellence."
    )
    db.add(me)
    
    # Define Experience Blocks
    blocks = [
        # === SKILLS SUMMARY (ALWAYS INCLUDED) ===
        {
            "title": "Technical Skills Portfolio",
            "company": "Edward Baitsewe",
            "content": """**Backend:** PHP (Laravel 9-11), Python (Django, Flask, FastAPI), RESTful API Design, Eloquent ORM, SQLAlchemy
**Frontend:** JavaScript (Alpine.js, Vue.js, React), Inertia.js, Blade Templates, Tailwind CSS, Bootstrap, Responsive Design
**Databases:** MySQL, MariaDB, PostgreSQL + PostGIS, SQLite, Redis
**Search & AI:** Typesense, Vector Search, pgvector, RAG Architecture, OpenAI API, Embeddings, LLM Integration
**DevOps & Infrastructure:** Docker, Docker Compose, Nginx, GitHub Actions, CI/CD Pipelines, Blue/Green Deployment, VPS Management
**Cloud & Services:** AWS (SES, SNS), Cloudflare CDN, Let's Encrypt SSL
**Tools & Platforms:** Git, GitHub, Linux (Ubuntu/Debian), SSH, Bash Scripting
**Specialized:** OAuth 2.0 (Google/Facebook), Geospatial Data (PostGIS), Image Optimization (WebP, Intervention Image), Multi-tenant Architecture, ETL Pipelines, Web Scraping (BeautifulSoup4)
**Methodologies:** Agile, Test-Driven Development, Code Review, Documentation, API Design""",
            "tags": ["PHP", "Laravel", "Python", "Django", "Flask", "FastAPI", "JavaScript", "Alpine.js", "Vue.js", "React", "Inertia.js", "Blade", "Tailwind CSS", "MySQL", "PostgreSQL", "PostGIS", "Redis", "Typesense", "Vector Search", "RAG", "OpenAI", "Docker", "Nginx", "GitHub Actions", "CI/CD", "AWS", "OAuth 2.0", "Geospatial"],
            "block_type": "skills_summary",
            "priority": "1"
        },
        
        # === PILLAR PROJECTS (ALWAYS INCLUDED) ===
        {
            "title": "ActuallyFind – Core Platform",
            "company": "ActuallyFind (Monate Media)",
            "content": """**Production Marketplace:** Full-stack vehicle marketplace serving bikes, cars, and commercial vehicles with real users and listings, deployed on VPS with zero-downtime deployments.

**Tech Stack:** **Laravel 11**, **PostgreSQL + PostGIS**, **Typesense**, **Alpine.js**, **Docker**, **GitHub Actions**

**Search Architecture:** Integrated **Typesense** vector search with 25-field schema, faceted search on 13+ attributes (manufacturer, model, price, year, mileage, fuel type), sub-500ms query response times via client-side rendering with Axios.

**Geospatial Features:** **PostgreSQL + PostGIS** for radius-based location filtering using `ST_DistanceSphere` calculations, dynamic range slider, "closest to me" sorting with real-time distance display.

**Database Design:** 30+ tables with hierarchical taxonomy (Sections → Categories → Vehicle Types), normalized lookups (transmissions, drivetrains, colors), many-to-many relationships (features, ownership paperwork).

Production: https://actuallyfind.com/

**Demo Available:**
| Field | Value |
|-------|-------|
| URL | https://dealership.monatemedia.com/ |
| Email | user@example.com |
| Password | password |
| Test VIN | AFAVXDL44VR135790 |

GitHub (Private): https://github.com/monatemedia/dealership""",
            "tags": ["Laravel", "PostgreSQL", "PostGIS", "Typesense", "Vector Search", "Geospatial", "Alpine.js", "Blade", "Axios", "Production SaaS", "Marketplace"],
            "block_type": "pillar_project",
            "priority": "1"
        },
        {
            "title": "ActuallyFind – DevOps & Infrastructure",
            "company": "ActuallyFind (Monate Media)",
            "content": """**Zero-Downtime Deployment:** Engineered **Blue/Green deployment** strategy via custom Bash scripts and **GitHub Actions CI/CD**, atomic container swaps using nginx-proxy VIRTUAL_HOST switching, health checks with automatic rollback on failures.

**Infrastructure:** **Docker Compose** orchestration across staging/production environments, **Docker** networking with `proxy-network` for container isolation, environment-specific configuration (.env files).

**Image Processing:** Async image processing using **Laravel Queues** and **Intervention Image**, achieved ~77× compression (1.7MB → 22KB WebP) with **Spatie Image Optimizer**, UUID-based filenames, CDN delivery via **Cloudflare**.

**Production Monitoring:** Custom Artisan commands for Typesense cluster management, real-time image processing status API, vehicle search analytics.

**Security:** **Let's Encrypt SSL** with auto-renewal, **AWS SES** email verification with **SNS** webhook handling for bounces/complaints, Laravel policy-based authorization.""",
            "tags": ["Docker", "Docker Compose", "GitHub Actions", "CI/CD", "Blue/Green Deployment", "Nginx", "Bash Scripting", "Laravel Queues", "Image Optimization", "WebP", "Cloudflare CDN", "AWS SES", "AWS SNS", "SSL", "DevOps"],
            "block_type": "pillar_project",
            "priority": "1"
        },
        {
            "title": "Vector CV – AI-Powered Resume Synthesizer",
            "company": "Personal Project",
            "content": """**RAG Architecture:** Built an AI-powered resume generation system using **FastAPI**, **PostgreSQL + pgvector**, and **OpenAI embeddings** for semantic matching of experience blocks to job descriptions.

**Vector Search:** Implemented cosine similarity search to automatically select the most relevant experience blocks for each job application, ensuring tailored CVs without manual curation.

**Hybrid Selection Logic:** Combines vector similarity with skill-matching and priority-based selection to ensure comprehensive skill coverage in generated CVs.

**LLM Integration:** Designed sophisticated prompt engineering system with few-shot examples and anti-hallucination guards to maintain consistent voice and prevent fabricated credentials.

**Tech Stack:** **Python**, **FastAPI**, **SQLAlchemy**, **pgvector**, **OpenAI API**, **Streamlit** for UI, **Docker Compose** for local development.

**Key Innovation:** Uses embeddings to understand job requirements and automatically ranks candidate experience by relevance, then generates tailored CVs and cover letters matching the candidate's writing style.

GitHub: https://github.com/monatemedia/vector-cv""",
            "tags": ["Python", "FastAPI", "PostgreSQL", "pgvector", "OpenAI", "RAG", "Vector Search", "LLM", "Prompt Engineering", "Streamlit", "Docker Compose", "SQLAlchemy", "AI"],
            "block_type": "pillar_project",
            "priority": "1"
        },
        
        # === SUPPORTING PROJECTS ===
        {
            "title": "Project Management CRM – Laravel + React + Inertia.js",
            "company": "Monate Media",
            "content": """**Production CRM System:** Built a full-stack project and task management system using **Laravel 11**, **React**, and **Inertia.js**, currently in production use for managing client relationships.

**React + Inertia.js Architecture:** Server-driven SPA using Inertia.js for seamless page transitions, reusable React components (TableHeading, Pagination, SelectInput), real-time filtering/sorting without page reloads.

**Key Features:** Project and task CRUD with image uploads, multi-field search and sort (name, status, date), role-based task assignment, dashboard with task statistics (pending/in-progress/completed), "My Tasks" filtered view.

**Frontend Engineering:** **Tailwind CSS** dark mode theme, sortable table headers with ascending/descending toggles, search filters with debouncing, pagination with query string persistence, color-coded status badges.

**Database Design:** Relational schema with Projects, Tasks, and Users tables using foreign key constraints with audit columns (created_by, updated_by). Tasks support priority levels (low/medium/high) and status tracking.

GitHub: https://github.com/monatemedia/laravel11-react-inertia""",
            "tags": ["Laravel 11", "React", "Inertia.js", "Eloquent ORM", "Form Request Validation", "API Resources", "Tailwind CSS", "MySQL", "Image Uploads", "SPA", "CRUD", "CRM", "Production"],
            "block_type": "supporting_project",
            "priority": "2"
        },
        {
            "title": "VinScape – VIN Decoder Microservice",
            "company": "Personal Project",
            "content": """**Microservice Architecture:** Built a **Flask**-based microservice for decoding and generating Vehicle Identification Numbers (VINs) using ISO 3779 standards, demonstrating polyglot architecture (PHP/Python) for specialized business logic.

**Data Pipeline:** Engineered an ETL pipeline that scrapes Wikipedia's WMI codes using **BeautifulSoup4**, normalizes 2,300+ manufacturers and 250+ countries/regions, populates **SQLite** database with proper relational schema.

**Algorithm Implementation:** Implemented check digit validation using transliteration tables and modulo-11 calculation for North American VINs, achieving 100% accuracy against ISO 3779 standard.

**Tech Stack:** **Python/Flask**, **SQLAlchemy ORM**, **BeautifulSoup4** for web scraping, **SQLite**, with static assets served via Flask routes.

**Key Features:** VIN decoder, random VIN generator with valid check digits, manufacturer logo associations, factory review interface.

GitHub: https://github.com/monatemedia/vinscape""",
            "tags": ["Python", "Flask", "SQLAlchemy", "BeautifulSoup4", "Web Scraping", "ETL Pipeline", "SQLite", "API Design", "ISO Standards", "Algorithm Implementation", "Microservices"],
            "block_type": "supporting_project",
            "priority": "2"
        },
        {
            "title": "Denlin – Docker Engine on Linux CLI Tool",
            "company": "Open Source",
            "content": """**DevOps Automation:** Built a comprehensive **Bash** CLI tool for managing containerized applications on VPS, automating the entire deployment workflow from local development to production.

**Infrastructure Management:** Engineered scripts to orchestrate **Docker**, **Nginx reverse proxy**, **Let's Encrypt SSL**, and **GitHub Actions CI/CD** pipelines, reducing deployment time from hours to minutes.

**Key Features:** User creation with SSH key-pair authentication, automated Nginx proxy setup with SSL certificates, **GitHub Container Registry** integration, Docker Compose template generation, one-command container deployment.

**Developer Experience:** Created interactive CLI menu system with 15+ automation modules, auto-updating script distribution via Git, comprehensive GitHub Wiki documentation.

**Architecture:** Implements Docker networking with `proxy-network` for container isolation, environment-specific configuration (.env files), blue/green deployment patterns for zero-downtime updates.

**Real-World Usage:** Currently manages multiple production applications (ActuallyFind, AchievementHQ) on resource-constrained VPS.

GitHub: https://github.com/monatemedia/docker-engine-on-linux""",
            "tags": ["Bash", "Docker", "Docker Compose", "Nginx", "Let's Encrypt", "SSL/TLS", "GitHub Actions", "CI/CD", "GitHub Container Registry", "VPS Management", "SSH", "Linux", "Ubuntu", "DevOps Automation", "Infrastructure as Code", "Reverse Proxy", "CLI Tools"],
            "block_type": "supporting_project",
            "priority": "2"
        },
        {
            "title": "AchievementHQ – Social Achievement Tracker",
            "company": "Personal Project",
            "content": """**Social Platform:** Built a **Django**-based social network for users to track, share, and celebrate personal and professional achievements with timeline-based feeds.

**Full-Stack Features:** User authentication, CRUD operations for posts/comments, admin dashboard with full moderation capabilities, responsive **Bootstrap** UI with custom CSS timeline components.

**Database Design:** Relational schema using **Django ORM** with models for Users, Posts, Comments, and Polls, including approval workflows and soft-delete patterns.

**DevOps:** Containerized with **Docker** and **Docker Compose** for deployment on VPS, configured with production/local environment separation (.env files), set up with **Nginx** reverse proxy.

**Demo System:** Created `demo.py` script that seeds database with sample users, posts, and comments for instant testing.

GitHub: https://github.com/monatemedia/python-django-achievementhq""",
            "tags": ["Python", "Django", "Django ORM", "SQLite", "Bootstrap", "Docker", "Docker Compose", "Nginx", "Authentication", "CRUD", "Social Platform", "Timeline UI", "Admin Dashboard"],
            "block_type": "supporting_project",
            "priority": "3"
        },
        {
            "title": "LaraGigs – Laravel Job Board",
            "company": "Personal Project",
            "content": """**Full-Stack CRUD Application:** Built a job listing platform for Laravel developer positions using **Laravel 9**, implementing complete RESTful resource controllers with authentication and authorization.

**Key Features:** User registration/login with session management, job posting CRUD with image uploads, search/filter system using Laravel query scopes, pagination, flash messaging.

**Authorization Logic:** Ownership-based authorization—users can only edit/delete their own listings, enforced through middleware (`auth`, `guest`) and manual authorization Guards.

**Database Design:** Relational schema with `users` and `listings` tables using foreign key constraints with cascade deletes, demonstrating understanding of Eloquent relationships (`belongsTo`).

**Advanced Laravel Features:** Custom query scopes for tag and search filtering, form request validation with `Rule::unique()`, factory seeders for test data, Blade component architecture.

**Frontend:** **Tailwind CSS** with Blade components (`<x-listing-card>`, `<x-layout>`), demonstrating component-based templating.

GitHub: https://github.com/monatemedia/laragigs""",
            "tags": ["Laravel", "PHP", "Blade Templates", "Eloquent ORM", "MySQL", "Authentication", "Authorization", "CRUD", "RESTful API", "Query Scopes", "Form Validation", "Factory Seeders", "Tailwind CSS", "Docker"],
            "block_type": "supporting_project",
            "priority": "4"
        },
        {
            "title": "Mortgage Calculator – Streamlit Financial Tool",
            "company": "Personal Project",
            "content": """**Financial Modeling:** Built an interactive mortgage calculator using **Python/Streamlit** with **NumPy Financial** for accurate amortization calculations, demonstrating understanding of time-value-of-money principles.

**Key Features:** Real-time monthly payment calculations, principal vs. interest breakdown visualization, cumulative interest tracking, complete amortization table generation with date-based scheduling using **Pandas**.

**Algorithm Implementation:** Implemented financial formulas using `numpy_financial` (`pmt`, `ppmt`, `ipmt`) with period-by-period balance tracking and edge-case handling for zero balances.

**Data Visualization:** Interactive line charts showing payment breakdown evolution and cost of credit accumulation, with Markdown tables for summary statistics.

**User Experience:** Sidebar parameter controls (loan amount: 50K-50M, interest: 0-20%, term: 5-30 years, start date picker) with instant recalculation and responsive chart updates.

**Deployment:** Multi-stage Dockerfile with non-root user security, automated CI/CD via **GitHub Actions**, deployed to VPS with Nginx reverse proxy and **Let's Encrypt SSL**.

GitHub: https://github.com/monatemedia/python-streamlit-mortgage-calculator""",
            "tags": ["Python", "Streamlit", "Pandas", "NumPy", "NumPy Financial", "Data Visualization", "Financial Modeling", "Amortization", "Docker", "Multi-stage Dockerfile", "GitHub Actions", "CI/CD", "Nginx", "Let's Encrypt"],
            "block_type": "supporting_project",
            "priority": "5"
        },
        
        # === EMPLOYMENT HISTORY ===
        {
            "title": "Full Stack Developer & Fintech Solutions Architect",
            "company": "Monate Media",
            "content": """**Fintech Ecosystem Engineering:** Specialized in deploying and customizing **Akaunting** (open-source Laravel-based ERP) to automate invoicing, expense tracking, and real-time financial reporting for SMEs.

**Custom CMS & ERP Integration:** Architected seamless data pipelines between **WordPress/WooCommerce** and **Akaunting**, ensuring automated synchronization of sales, inventory, and customer records.

**Lead Generation Systems:** Built high-conversion financial landing pages and custom WordPress tools integrated with third-party CRMs to capture and qualify high-value leads.

**Infrastructure & Security:** Managed full-stack deployments on Linux VPS using **Nginx**, **Docker**, and **SSL** hardening, ensuring 99.9% uptime for business-critical financial applications.

**Technical SEO:** Optimized web assets for performance, focusing on Core Web Vitals to improve search rankings and user retention for financial services clients.

**Duration:** May 2021 – Present""",
            "tags": ["Akaunting", "Laravel", "WordPress", "Fintech", "ERP Integration", "WooCommerce", "PHP", "Vue.js", "MySQL", "Nginx", "DevOps", "Financial Automation"],
            "block_type": "employment",
            "priority": "1"
        },
        
        # === EDUCATION ===
        {
            "title": "Education & Certifications",
            "company": "Academic Background",
            "content": """**Postgraduate Diploma in Financial Planning** – University of the Free State (2017)
**MERSETA National Qualification: Auto Technician** – Westlake Technical College (2007)
**Regulatory Examination (RE5)** – FSCA / Moonstone
**Online Technical Certifications:** Advanced Laravel Ecosystem, PHP, and Python (StudioWeb, Teachable). Focused on modern DevOps, search optimization (Typesense/Algolia), and architecting scalable web applications.""",
            "tags": ["Education", "Postgrad", "Financial Planning", "MERSETA", "Technical Qualification", "RE5", "Laravel", "Python", "DevOps"],
            "block_type": "education",
            "priority": "1"
        }
    ]
    
    print("Generating embeddings and saving blocks...")
    for item in blocks:
        # Create a string for the LLM to 'understand' the context
        combined_text = f"{item['title']} at {item['company']}: {item['content']} Keywords: {', '.join(item['tags'])}"
        
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
    db.close()
    print("✅ Seeding complete! Your RAG system is now fully optimized.")
    print(f"📚 Added {len(blocks)} experience blocks with proper categorization:")
    print("   - 1 Skills Summary (always included)")
    print("   - 3 Pillar Projects (always included)")
    print("   - 6 Supporting Projects (selected by relevance)")
    print("   - 1 Employment History")
    print("   - 1 Education")

if __name__ == "__main__":
    from database import init_db
    # 1. Force the extension and table creation properly
    init_db() 
    # 2. Then run the seed logic
    seed_database()