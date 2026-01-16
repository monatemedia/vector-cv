import os
import uuid
from database import SessionLocal, engine
from models import ExperienceBlock, PersonalInfo, Base
from llm_service import generate_embedding

def seed_database():
    print("Starting database seeding...")
    db = SessionLocal()

    # 1. Clear existing data (Optional - use with caution)
    # Base.metadata.drop_all(bind=engine)
    # Base.metadata.create_all(bind=engine)

    # 2. Add Personal Info
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

    # 3. Define Experience Blocks (with accurate, detailed information)
    blocks = [
        {
    "title": "ActuallyFind – Vehicle Marketplace SaaS",
    "company": "ActuallyFind (Monate Media)",
    "content": """**Production Marketplace:** Built and currently operating a full-stack vehicle marketplace serving bikes, cars, and commercial vehicles with real users and listings, deployed on VPS with zero-downtime Blue/Green deployments.

**Advanced Search Architecture:** Integrated **Typesense** vector search engine with 25-field schema including geopoint filtering, faceted search on 13+ attributes (manufacturer, model, price, year, mileage, fuel type), and sub-500ms query response times via client-side rendering with Axios.

**Geospatial Features:** Implemented **PostgreSQL + PostGIS** for radius-based location filtering using `ST_DistanceSphere` calculations, dynamic range slider showing max distance to furthest listing, and "closest to me" sorting with real-time distance display on vehicle cards.

**Image Processing Pipeline:** Engineered async image processing using **Laravel Queues** and **Intervention Image**, achieving ~77× compression (1.7MB → 22KB WebP) with **Spatie Image Optimizer** integration, UUID-based filenames, and sortable drag-and-drop gallery management.

**Complex Data Modeling:** Designed relational schema with 30+ tables including hierarchical taxonomy (Sections → Categories → Vehicle Types), normalized lookups (transmissions, drivetrains, colors), many-to-many relationships (features, ownership paperwork), and soft deletes with audit trails.

**DevOps Excellence:** Implemented zero-downtime **Blue/Green deployment** via custom Bash scripts and GitHub Actions CI/CD, atomic container swaps using nginx-proxy VIRTUAL_HOST switching, health checks, and Docker Compose orchestration across staging/production environments.

**Frontend Architecture:** Laravel **Blade** components with **Alpine.js** for reactive UI (infinite scroll, instant filters, watchlist hearts), vanilla CSS for performance, InstantSearch.js integration for real-time faceted search, and responsive mobile-first design.

**Authentication & Authorization:** Laravel Socialite OAuth 2.0 (Google/Facebook), AWS SES email verification with SNS webhook handling for bounces/complaints, policy-based authorization (VehiclePolicy), and profile completion flows.

**Production Monitoring:** Custom Artisan commands for Typesense cluster management, real-time image processing status API, vehicle search analytics, and Docker health checks with automatic rollback on deployment failures.

Production server at https://actuallyfind.com/

**Demo Available:** Staging server at https://dealership.monatemedia.com/
- Email: user@example.com
- Password: password
- Test VIN: AFAVXDL44VR135790

GitHub (Private): https://github.com/monatemedia/dealership""",
    "tags": ["Laravel", "PostgreSQL", "PostGIS", "Typesense", "Vector Search", "Geospatial", "GitHub Actions", "Docker", "Docker Compose", "Blue/Green Deployment", "Image Optimization", "WebP", "Intervention Image", "Spatie Image Optimizer", "Cloudflare CDN", "Alpine.js", "Blade Components", "Axios", "AWS SES", "AWS SNS", "OAuth 2.0", "Laravel Socialite", "Laravel Scout", "Laravel Queues", "Nginx", "InstantSearch.js", "Bash Scripting", "Production SaaS"]
        },
        {
            "title": "Vector CV – AI-Powered Resume Synthesizer",
            "company": "Personal Project",
            "content": """**RAG Architecture:** Built an AI-powered resume generation system using **FastAPI**, **PostgreSQL + pgvector**, and **OpenAI embeddings** for semantic matching of experience blocks to job descriptions.

**Vector Search:** Implemented cosine similarity search to automatically select the most relevant experience blocks for each job application, ensuring tailored CVs without manual curation.

**LLM Integration:** Designed sophisticated prompt engineering system with few-shot examples and anti-hallucination guards to maintain consistent voice and prevent fabricated credentials.

**Tech Stack:** **Python**, **FastAPI**, **SQLAlchemy**, **pgvector**, **Streamlit** for UI, **Docker Compose** for local development.

**Key Innovation:** Uses embeddings to understand job requirements and automatically ranks candidate experience by relevance, then generates tailored CVs and cover letters matching the candidate's writing style.

GitHub: https://github.com/monatemedia/vector-cv""",
            "tags": ["Python", "FastAPI", "PostgreSQL", "pgvector", "OpenAI", "RAG", "Vector Search", "LLM", "Prompt Engineering", "Streamlit", "Docker Compose", "SQLAlchemy"]
        },
        {
    "title": "VinScape – VIN Decoder Microservice",
    "company": "Personal Project",
    "content": """**Architecture:** Built a Flask-based microservice for decoding and generating Vehicle Identification Numbers (VINs) using ISO 3779 standards, demonstrating polyglot architecture (PHP/Python) for specialized business logic.

**Data Pipeline:** Engineered an ETL pipeline that scrapes Wikipedia's WMI codes, normalizes 2,300+ manufacturers and 250+ countries/regions, and populates a SQLite database with proper relational schema.

**Algorithm Implementation:** Implemented check digit validation using transliteration tables and modulo-11 calculation for North American VINs, achieving 100% accuracy against ISO 3779 standard.

**Tech Stack:** **Python/Flask**, **SQLAlchemy ORM**, **BeautifulSoup4** for web scraping, **SQLite**, with static assets served via Flask routes.

**Key Features:** VIN decoder, random VIN generator with valid check digits, manufacturer logo associations, factory review interface.

GitHub: https://github.com/monatemedia/vinscape""",
    "tags": ["Python", "Flask", "SQLAlchemy", "BeautifulSoup4", "Web Scraping", "ETL Pipeline", "SQLite", "API Design", "ISO Standards", "Algorithm Implementation", "Microservices", "Polyglot Architecture"]
        },
        {
    "title": "AchievementHQ – Social Achievement Tracker",
    "company": "Personal Project",
    "content": """**Social Platform:** Built a Django-based social network for users to track, share, and celebrate personal and professional achievements with timeline-based feeds.

**Full-Stack Features:** Implemented user authentication, CRUD operations for posts/comments, admin dashboard with full moderation capabilities, and responsive Bootstrap UI with custom CSS timeline components.

**Database Design:** Architected relational schema using Django ORM with models for Users, Posts, Comments, and Polls, including approval workflows and soft-delete patterns.

**DevOps:** Containerized with **Docker** and **Docker Compose** for deployment on VPS, configured with production/local environment separation (.env files), and set up with Nginx reverse proxy.

**Demo System:** Created `demo.py` script that seeds database with sample users, posts, and comments for instant testing—demonstrates understanding of developer experience and onboarding.

**Demo Available:** Offline by default (resource optimization), can be brought online on request via Docker Compose.

GitHub: https://github.com/monatemedia/python-django-achievementhq""",
    "tags": ["Python", "Django", "Django ORM", "SQLite", "Bootstrap", "Docker", "Docker Compose", "Nginx", "Authentication", "CRUD", "Social Platform", "Timeline UI", "Admin Dashboard", "Environment Management"]
        },
        {
    "title": "Denlin – Docker Engine on Linux CLI Tool",
    "company": "Open Source",
    "content": """**DevOps Automation:** Built a comprehensive Bash CLI tool for managing containerized applications on VPS, automating the entire deployment workflow from local development to production.

**Infrastructure Management:** Engineered scripts to orchestrate **Docker**, **Nginx reverse proxy**, **Let's Encrypt SSL**, and **GitHub Actions CI/CD** pipelines, reducing deployment time from hours to minutes.

**Key Features:** User creation with SSH key-pair authentication, automated Nginx proxy setup with SSL certificates, GitHub Container Registry integration, Docker Compose template generation, and one-command container deployment.

**Developer Experience:** Created interactive CLI menu system with 15+ automation modules, auto-updating script distribution via Git, and comprehensive GitHub Wiki documentation—demonstrating focus on tool usability and maintainability.

**Architecture:** Implements Docker networking with `proxy-network` for container isolation, environment-specific configuration (.env files), and blue/green deployment patterns for zero-downtime updates.

**Real-World Usage:** Currently manages multiple production applications (ActuallyFind, AchievementHQ) on resource-constrained VPS, proving cost-effective self-hosting at scale.

GitHub: https://github.com/monatemedia/docker-engine-on-linux""",
    "tags": ["Bash", "Docker", "Docker Compose", "Nginx", "Let's Encrypt", "SSL/TLS", "GitHub Actions", "CI/CD", "GitHub Container Registry", "VPS Management", "SSH", "Linux", "Ubuntu", "DevOps Automation", "Infrastructure as Code", "Reverse Proxy", "CLI Tools"]
        },
        {
    "title": "LaraGigs – Laravel Job Board",
    "company": "Personal Project",
    "content": """**Full-Stack CRUD Application:** Built a job listing platform for Laravel developer positions using **Laravel 9**, implementing complete RESTful resource controllers with authentication and authorization.

**Key Features:** User registration/login with session management, job posting CRUD with image uploads (stored via `storage:link`), search/filter system using Laravel query scopes, pagination, and flash messaging for user feedback.

**Authorization Logic:** Implemented ownership-based authorization—users can only edit/delete their own listings, enforced through middleware (`auth`, `guest`) and manual authorization Guards in controllers.

**Database Design:** Relational schema with `users` and `listings` tables using foreign key constraints with cascade deletes (`user_id` → `users.id`), demonstrating understanding of Eloquent relationships (`belongsTo`).

**Advanced Laravel Features:** Custom query scopes for tag and search filtering, form request validation with `Rule::unique()`, factory seeders for test data generation, and Blade component architecture for reusable UI elements.

**Frontend:** Tailwind CSS with Blade components (`<x-listing-card>`, `<x-layout>`), demonstrating component-based templating and modern utility-first CSS.

**Deployment:** Dockerized with custom entrypoint scripts, managed via Docker Compose on VPS. Demo available on request.

GitHub: https://github.com/monatemedia/laragigs""",
    "tags": ["Laravel", "PHP", "Blade Templates", "Eloquent ORM", "MySQL", "Authentication", "Authorization", "CRUD", "RESTful API", "Query Scopes", "Form Validation", "Factory Seeders", "Tailwind CSS", "Docker", "Docker Compose", "Middleware"]
        },
        {
    "title": "Mortgage Calculator – Streamlit Financial Tool",
    "company": "Personal Project",
    "content": """**Financial Modeling:** Built an interactive mortgage calculator using **Python/Streamlit** with **NumPy Financial** for accurate amortization calculations, demonstrating understanding of time-value-of-money principles.

**Key Features:** Real-time monthly payment calculations, principal vs. interest breakdown visualization, cumulative interest tracking, and complete amortization table generation with date-based scheduling using **Pandas**.

**Algorithm Implementation:** Implemented financial formulas using `numpy_financial` (`pmt`, `ppmt`, `ipmt`) with period-by-period balance tracking and edge-case handling for zero balances, ensuring calculation accuracy across 5-30 year loan terms.

**Data Visualization:** Interactive line charts showing payment breakdown evolution and cost of credit accumulation over time, with Markdown tables for summary statistics (first vs. final payments, total cost).

**User Experience:** Sidebar parameter controls (loan amount: 50K-50M, interest: 0-20%, term: 5-30 years, start date picker) with instant recalculation and responsive chart updates.

**Deployment:** Multi-stage Dockerfile with non-root user security, automated CI/CD via GitHub Actions, deployed to VPS with Nginx reverse proxy and Let's Encrypt SSL.

**Demo Available:** Offline by default (resource optimization), can be brought online on request via Docker Compose.

GitHub: https://github.com/monatemedia/python-streamlit-mortgage-calculator""",
    "tags": ["Python", "Streamlit", "Pandas", "NumPy", "NumPy Financial", "Data Visualization", "Financial Modeling", "Amortization", "Docker", "Multi-stage Dockerfile", "GitHub Actions", "CI/CD", "Nginx", "Let's Encrypt"]
        },
        {
    "title": "Project Management CRM – Laravel + React + Inertia.js",
    "company": "Monate Media",
    "content": """**Production CRM System:** Built a full-stack project and task management system using **Laravel 11**, **React**, and **Inertia.js**, currently in production use on shared hosting for managing client relationships.

**Advanced Laravel Features:** Implemented resource controllers with Form Request validation, API Resources for data transformation, Eloquent relationships (hasMany, belongsTo) with proper foreign key constraints, and audit trail tracking (created_by, updated_by).

**React + Inertia.js Architecture:** Server-driven SPA using Inertia.js for seamless page transitions, reusable React components (TableHeading, Pagination, SelectInput), and real-time filtering/sorting without page reloads.

**Key Features:** Project and task CRUD with image uploads, multi-field search and sort (name, status, date), role-based task assignment, dashboard with task statistics (pending/in-progress/completed), "My Tasks" filtered view, and flash message notifications.

**Database Design:** Relational schema with Projects, Tasks, and Users tables using foreign key constraints with audit columns. Tasks support priority levels (low/medium/high), status tracking (pending/in-progress/completed), and assignment to users.

**Frontend Engineering:** Tailwind CSS dark mode theme, sortable table headers with ascending/descending toggles, search filters with debouncing, pagination with query string persistence, and color-coded status badges.

**Production Deployment:** Currently running on shared hosting with manual deployment, demonstrating real-world application in daily client relationship management workflows.

GitHub: https://github.com/monatemedia/laravel11-react-inertia""",
    "tags": ["Laravel 11", "React", "Inertia.js", "Eloquent ORM", "Form Request Validation", "API Resources", "Tailwind CSS", "MySQL", "Image Uploads", "SPA", "CRUD", "Authentication", "Authorization", "Pagination", "Search & Filter", "Sortable Tables", "CRM", "Production"]
        },
        {
    "title": "Full Stack Developer & Fintech Solutions Architect",
    "company": "Monate Media",
    "content": """**Fintech Ecosystem Engineering:** Specialized in deploying and customizing **Akaunting** (open-source Laravel-based ERP) to automate invoicing, expense tracking, and real-time financial reporting for SMEs.
**Custom CMS & ERP Integration:** Architected seamless data pipelines between **WordPress/WooCommerce** and **Akaunting**, ensuring automated synchronization of sales, inventory, and customer records.
**Lead Generation Systems:** Built high-conversion financial landing pages and custom WordPress tools integrated with third-party CRMs to capture and qualify high-value leads.
**Infrastructure & Security:** Managed full-stack deployments on Linux VPS using **Nginx**, **Docker**, and **SSL** hardening, ensuring 99.9% uptime for business-critical financial applications.
**Technical SEO:** Optimized web assets for performance, focusing on Core Web Vitals to improve search rankings and user retention for financial services clients.
**Duration:** May 2021 – Present""",
    "tags": ["Akaunting", "Laravel", "WordPress", "Fintech", "ERP Integration", "WooCommerce", "PHP", "Vue.js", "MySQL", "Nginx", "DevOps", "Financial Automation"]
        },
        {
        "title": "Commercial Insurance Agent",
        "company": "OUTsurance",
        "content": """**Commercial Risk Management:** Prospected and closed high-value commercial insurance accounts, conducting deep-dive risk profile analysis for SMEs to tailor protection strategies.
**Product Expertise:** Focused exclusively on short-term commercial and personal insurance, protecting business assets against fire, accidental loss, theft, and flood damage.
**Stakeholder Engagement:** Delivered professional client presentations on product benefits and stringent regulatory compliance requirements.
**Duration:** March 2020 – April 2021""",
        "tags": ["Commercial Insurance", "Short-term Insurance", "Risk Assessment", "SME Relations", "Sales Strategy", "Compliance"]
        },
        {
        "title": "Financial Advisor",
        "company": "Old Mutual Life",
        "content": """**Portfolio Growth:** Achieved 21% Year-over-Year growth in intermediary portfolio for three consecutive years through strategic acquisition and high-stakes relationship management.
**Investment & Retirement Planning:** Expert in Collective Investment Schemes (Unit Trusts), LISPs, and Tax-Free Savings. Managed complex transitions from Retirement Annuities to Living/Life Annuity contracts.
**Corporate Solutions:** Implemented Deferred and Preferred Compensation strategies (Endowments/Cessions) to help corporate clients with key employee retention.
**Estate & Risk Planning:** Specialized in Wills, Trusts, and comprehensive Life/Disability/Severe Illness cover.
**Financial Education:** Conducted large-scale presentation sessions, simplifying complex market trends and investment concepts for retail and HNW clients.
**Duration:** August 2011 – February 2020""",
        "tags": ["Wealth Management", "Unit Trusts", "Retirement Planning", "Estate Planning", "Employee Benefits", "Key Person Insurance", "Client Retention", "Public Speaking"]
        },
        {
        "title": "Financial Advisor",
        "company": "Standard Bank Financial Consultancy",
        "content": """**Business Development:** Built and managed diverse client portfolios, identifying cross-selling opportunities for tailored financial products including Education Plans and Offshore Investments.
**Business Assurance:** Advised on Buy and Sell Contracts and Contingency Insurance to cover personal liability on business expansion loans.
**Operational Excellence:** Collaborated with internal banking teams to streamline onboarding processes, significantly reducing turnaround times and enhancing customer experience.
**Needs Analysis:** Conducted rigorous financial needs analyses (FNA) to align banking products with long-term client wealth goals.
**Duration:** March 2008 – July 2011""",
        "tags": ["Retail Investments", "Business Assurance", "Buy & Sell Agreements", "Offshore Investments", "Financial Analysis", "Banking Relations"]
        },
        {
        "title": "Sales and Arrears Consultant",
        "company": "Capitec Bank",
        "content": """**Credit Risk Management:** Managed the non-performing loans (NPL) ratio for the lending book of Capitec’s largest urban branch (Riebeek Street, Cape Town CBD).
**Client Acquisition:** Engaged retail clients to provide loan conversions and account solutions, consistently meeting high-volume sales targets.
**Debt Recovery & Negotiation:** Developed high-level negotiation skills while managing arrears and maintaining client relationships under financial stress.
**Duration:** April 2007 – January 2008""",
        "tags": ["Credit Risk", "Loan Conversions", "Arrears Management", "Debt Negotiation", "Retail Banking", "Financial Sales"]
        },
        {
    "title": "BMW Qualified Auto Technician (Apprenticeship)",
    "company": "Donford BMW & Westlake Technical College",
    "content": """**Accelerated Technical Certification:** Successfully completed a rigorous 4-year MERSETA apprenticeship program in just 3 years, demonstrating exceptional technical aptitude and fast-paced learning.
**Automotive Engineering:** Gained deep hands-on experience in diagnostic troubleshooting, mechanical repairs, and electronic systems within the BMW premium vehicle ecosystem.
**Theoretical Foundation:** Completed advanced theoretical studies at Westlake Technical College (Tokai), specializing in internal combustion engines, drivetrain logic, and automotive electronics.
**Professional Transition:** Voluntarily transitioned from technical engineering into the financial services sector to pursue business development and portfolio management.
**Duration:** March 2004 – March 2007""",
    "tags": ["MERSETA", "BMW Certified", "Automotive Engineering", "Diagnostics", "Technical Problem Solving", "Process Optimization", "Accelerated Learning"]
        },
        {
    "title": "Education & Certifications",
    "company": "Academic Background",
    "content": """**Postgraduate Diploma in Financial Planning** – University of the Free State (2017)
**MERSETA National Qualification: Auto Technician** – Westlake Technical College (2007)
**Regulatory Examination (RE5)** – FSCA / Moonstone
**Online Technical Certifications:** Advanced Laravel Ecosystem, PHP, and Python (StudioWeb, Teachable). 
Focused on modern DevOps, search optimization (Typesense/Algolia), and architecting scalable web applications.""",
    "tags": ["Education", "Postgrad", "Financial Planning", "MERSETA", "Technical Qualification", "RE5", "Laravel", "Python", "DevOps"]
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
            embedding=vector
        )
        db.add(block)

    db.commit()
    db.close()
    print("✅ Seeding complete! Your RAG system is now fully 'Edward-aware'.")
    print("📚 Added 6 experience blocks including education information.")

if __name__ == "__main__":
    seed_database()