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
* **Automated Nginx-Proxy:** Seamlessly integrated with the VPS proxy network for SSL (Let's Encrypt) and automated routing.

## 🚀 Key Features

* ✅ **Semantic Master Profile** – Store your work history as high-dimensional vectors.
* ✅ **Hybrid Retrieval** – Combines vector similarity and project priority logic.
* ✅ **Dynamic CV Synthesis** – Generates resumes in your exact voice using few-shot prompting.
* ✅ **Administrative Panel** – Full CRUD interface for experience blocks at `/admin`.
* ✅ **CI/CD Ready** – Automated deployment to VPS via GitHub Actions and GHCR.
* ✅ **API Logging** – Comprehensive OpenAI API request/response logging for debugging and cost monitoring.

## 🛠️ Technical Implementation

### The Vector Engine

The system utilizes **Cosine Distance** calculations within PostgreSQL to rank experience blocks:

* **Embedding Model:** `text-embedding-3-small` (1024 Dimensions).
* **Vector Ops:** Performed natively in SQL via `pgvector`.

### OpenAI API Logging & Monitoring

Vector CV includes built-in logging for all OpenAI API interactions:

* **📊 Request/Response Capture:** Every API call is logged with full context
* **💰 Token Usage Tracking:** Monitor costs with detailed token counts per operation
* **⏱️ Performance Metrics:** Track execution time for each API call
* **🐛 Error Logging:** Captures failures with complete error context
* **📁 Daily Log Files:** Automatically organized in `api_logs/openai_api_YYYY-MM-DD.log`

#### Log Format Example

```
🔵 REQUEST [20260202_143025_123456] - 2026-02-02 14:30:25.123
Operation: generate_tailored_cv
Model: gpt-4-turbo-preview

📨 Messages:
    [SYSTEM]:
      You are Edward Baitsewe's expert CV writer...
    [USER]:
      Generate CV for Full Stack Developer at TechCorp...

🟢 RESPONSE [20260202_143025_123456] - 2026-02-02 14:30:28.456
Model: gpt-4-turbo-preview
Usage:
  - Prompt tokens: 2847
  - Completion tokens: 1523
  - Total tokens: 4370

💬 Choice 0:
  {
    "header": {
      "name": "Edward Baitsewe",
      "title": "Full Stack Developer",
      ...
    }
  }

⏱️ [2026-02-02 14:30:28] generate_tailored_cv completed in 3333.45ms
```

#### Monitored Operations

1. **generate_embedding** - Text-to-vector conversions
2. **extract_skills_from_job** - Skill extraction from job descriptions
3. **analyze_skills_gap** - Skills gap analysis
4. **generate_tailored_cv** - CV generation
5. **generate_cover_letter** - Cover letter generation

#### Log Analysis Commands

```bash
# View today's logs in real-time
tail -f api_logs/openai_api_$(date +%Y-%m-%d).log

# Count total API calls
grep "🔵 REQUEST" api_logs/*.log | wc -l

# Calculate total tokens used
grep "Total tokens:" api_logs/*.log | awk '{sum += $3} END {print sum}'

# Find errors
grep "❌ ERROR" api_logs/*.log

# Count operations by type
echo "CV generations:" $(grep "generate_tailored_cv completed" api_logs/*.log | wc -l)
echo "Cover letters:" $(grep "generate_cover_letter completed" api_logs/*.log | wc -l)
```

#### Cost Estimation

Using GPT-4 Turbo pricing (as of 2024):
- Input: $10 / 1M tokens
- Output: $30 / 1M tokens

```bash
# Estimate daily costs from logs
TOKENS=$(grep "Total tokens:" api_logs/openai_api_$(date +%Y-%m-%d).log | \
  awk '{sum += $3} END {print sum}')
echo "Estimated cost: \$$(echo "scale=2; $TOKENS * 20 / 1000000" | bc)"
```

#### Customizing Log Location

Set the `OPENAI_LOG_DIR` environment variable:

```bash
# In your .env file
OPENAI_LOG_DIR=/var/log/vector-cv
```

### DevOps & Orchestration

This project uses a production-grade deployment flow:

1. **CI:** GitHub Actions builds three distinct images (Backend, Streamlit, Frontend).
2. **Registry:** Images are versioned and stored in **GitHub Container Registry (GHCR)**.
3. **CD:** A remote `deploy-prod.sh` script on the VPS handles the container lifecycle, network attachment to the `proxy-network`, and database migrations.

## 📦 Local Deployment To Docker Desktop

1. **Clone the Repository:**
```bash
git clone https://github.com/monatemedia/vector-cv.git
cd vector-cv
```

2. **Configure Environment:**
```bash
# Make an .env file
cp .env.example .env
# At the very least add your OPENAI_API_KEY
```

3. **Create Your `json` Data:**
```bash
# Make your data file
cp my_data/my_data.json.example my_data/my_data.json
```

  Open `my_data/my_data.json` and update the file with your data. You may skip this step and use the admin UI later, or use the file you just created for testing.

4. **Launch the Stack:**
```bash
# Start dev app in detached mode
docker compose -f docker-compose.dev.yml up -d
```

  Common extra flags include `--build` to rebuild container.

  You can visit the app:
  - Fontend: http://localhost:3000
  - API Docs: http://localhost:3000/docs
  - Admin UI: http://localhost:3000/admin

  | Admin Username | Admin Password |
  | -------------- | -------------- |
  | user           | password       |

  You may also choose to use the admin UI to create your data for the app.

5. **Verify Your `json` Data (If Applicable)**
```bash
# Check for your data in the container
docker exec -it vector-cv-backend-1 ls my_data
```

  You should see your data `json` printed to the screen, example, `my_data.json`.

6. **Seed Data**
```bash
# Call seed_data.py script on your data json
docker compose exec backend \
  python seed_data.py my_data/my_data.json
```

7. **View API Logs (Optional)**
```bash
# Monitor OpenAI API calls in real-time
docker compose exec backend tail -f api_logs/openai_api_$(date +%Y-%m-%d).log
```

8. **Stop and Remove App:**
```bash
# Stop container
docker compose -f docker-compose.dev.yml down
```

  Common extra flags include `-v` to remove volumes and `--rmi all` to remove all containers and flush cache     

## 📦 Production Deployment & Configuration

### GitHub Secrets Required

To use the automated deployment, ensure the following secrets are set in your repository:

* `WORK_DIR`: Working directory.
* `AUTH_USERNAME`: Admin username.
* `AUTH_PASSWORD`: Admin password.
* `AUTH_NAME`: Admin name for panel.
* `HOST` & `USER`: VPS SSH credentials.
* `SSH_KEY`: Private key for remote access.
* `OPENAI_API_KEY`: API key for RAG operations.
* `ALLOWED_ORIGINS`: Allowed origins for API calls.
* `PAT`: GitHub token with write:packages permission.
* `DB_PASSWORD`: Database password for vector database.
* `COOKIE_KEY`: Strong key for frontend to connect to api.
* `ADMIN_API_KEY`: Strong key for admin UI to connect to api.

### Production Environment

The application is mapped to `edward.monatemedia.com` with the following internal routing:

* **`/`**: React Frontend
* **`/admin`**: Streamlit Admin Panel
* **`/docs`**: FastAPI Backend Swagger UI Docs

### Pushing A New Release To Production

```bash
# Create an annotated tag with a message
git tag -a v1.0.0 -m "Initial production release"
# Push tagged release to the repo to trigger GitHub Actions
git push origin v1.0.0
```

### Reusing Annotated Tags From Failed Deployments

```bash
# Delete the failed tag
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0

# Re-create and push
git tag -a v1.0.0 -m "Initial production release"
git push origin v1.0.0
```

## 🎨 Workflow

1. **Seed Data:** Input contact details and professional summary.
2. **Vectorize Experience:** Add work history blocks; the system generates embeddings on save.
3. **Define Style:** Set guardrails (e.g., "Must follow STAR method").
4. **Synthesize:** Paste a job description. The RAG engine retrieves relevant vectors and prompts GPT-4o to generate tailored materials.

## 🔍 Debugging & Monitoring

### API Logs

All OpenAI API interactions are automatically logged to `api_logs/` with the following information:
- Complete request/response payloads
- Token usage and costs
- Execution time
- Error details

**Security Note:** API logs contain sensitive data (personal information, job descriptions, API responses). These files are excluded from version control via `.gitignore` and should be handled securely.

### Log Retention

Consider implementing log rotation for production environments:

```bash
# Example: Delete logs older than 30 days (add to crontab)
0 0 * * * find /path/to/api_logs -name "*.log" -mtime +30 -delete
```

## 📚 Additional Documentation

For more detailed information about specific features:

- **API Logging:** See `LOGGING_README.md` for comprehensive logging documentation
- **Integration Guide:** See `INTEGRATION_GUIDE.md` for step-by-step setup instructions
- **Quick Reference:** See `QUICK_REFERENCE.md` for common commands and workflows