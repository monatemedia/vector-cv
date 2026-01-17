# Vector CV React App Deployment Guide

## Overview

This guide will help you deploy the Vector CV React application to your VPS alongside the existing Streamlit app. The setup allows:

- **Streamlit app** (port 8501) - Your personal CV generation tool
- **React app** (port 3000) - Public-facing recruiter interface
- **FastAPI backend** (port 8010) - Shared by both apps

## Project Structure

```
resume-synthesizer/
├── main.py                 # FastAPI backend
├── streamlit_app.py        # Your personal admin interface
├── frontend/               # NEW - Public React app
│   ├── index.html
│   └── README.md
├── database.py
├── models.py
├── llm_service.py
├── seed_data.py
└── .env
```

## Deployment Options

### Option 1: Simple Static Hosting (Recommended for Start)

The React app is a single HTML file that can be served directly with Nginx.

**1. Create frontend directory:**
```bash
cd ~/resume-synthesizer
mkdir frontend
cd frontend
```

**2. Save the `index.html` file** (from the artifact I created)

**3. Configure Nginx:**
```nginx
# /etc/nginx/sites-available/vector-cv

server {
    listen 80;
    server_name cv.yourdomain.com;  # or your VPS IP

    # React Frontend
    location / {
        root /home/your-user/resume-synthesizer/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API Proxy
    location /api/ {
        proxy_pass http://localhost:8010/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**4. Enable site and restart Nginx:**
```bash
sudo ln -s /etc/nginx/sites-available/vector-cv /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**5. Add SSL (Let's Encrypt):**
```bash
sudo certbot --nginx -d cv.yourdomain.com
```

### Option 2: Docker Compose (Production Ready)

For a containerized setup with better isolation.

**1. Create `frontend/Dockerfile`:**
```dockerfile
FROM nginx:alpine

# Copy static files
COPY index.html /usr/share/nginx/html/

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
```

**2. Create `frontend/nginx.conf`:**
```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:8010/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**3. Update root `docker-compose.yml`:**
```yaml
version: '3.8'

services:
  database:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: resume_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: .
    depends_on:
      - database
    environment:
      DATABASE_URL: ${DATABASE_URL}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "8010:8010"
    volumes:
      - .:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8010 --reload

  frontend:
    build: ./frontend
    depends_on:
      - backend
    ports:
      - "3000:80"

  streamlit:
    build: .
    depends_on:
      - backend
    ports:
      - "8501:8501"
    command: streamlit run streamlit_app.py --server.port 8501

volumes:
  postgres_data:
```

**4. Start services:**
```bash
docker-compose up -d
```

## CORS Configuration

Update `main.py` to allow the React frontend:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Resume Synthesizer API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://cv.yourdomain.com",
        "http://your-vps-ip:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... rest of your code
```

## Environment Variables

Update your `.env` file:

```bash
# Database
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/resume_db

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Frontend URLs (for CORS)
FRONTEND_URL=https://cv.yourdomain.com
ADMIN_URL=http://localhost:8501
```

## DNS Setup

If using a custom domain:

1. Add A record: `cv.yourdomain.com` → Your VPS IP
2. Wait for DNS propagation (5-30 minutes)
3. Run Certbot for SSL

## Security Considerations

### 1. Rate Limiting

Add to Nginx config:

```nginx
limit_req_zone $binary_remote_addr zone=cv_limit:10m rate=5r/m;

server {
    # ... existing config
    
    location /api/applications {
        limit_req zone=cv_limit burst=2 nodelay;
        proxy_pass http://localhost:8010/api/applications;
    }
}
```

### 2. API Key Protection

The React app calls your backend, which uses YOUR OpenAI API key. To prevent abuse:

**Option A: Simple API Key Auth**
```python
# In main.py
from fastapi import Header, HTTPException

API_SECRET = os.getenv("API_SECRET", "your-secret-key")

@app.post("/api/applications")
async def create_job_application(
    app_data: JobApplicationCreate,
    x_api_key: str = Header(None),
    db: Session = Depends(get_db)
):
    if x_api_key != API_SECRET:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # ... rest of the code
```

Update React app to include header:
```javascript
const response = await fetch(`${API_URL}/api/applications`, {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'X-API-Key': 'your-secret-key'  // Share this only with trusted recruiters
  },
  body: JSON.stringify(formData)
});
```

**Option B: Usage Limits (Better)**
```python
# Track usage per IP
from collections import defaultdict
from datetime import datetime, timedelta

usage_tracker = defaultdict(list)
MAX_REQUESTS_PER_DAY = 3

@app.post("/api/applications")
async def create_job_application(
    app_data: JobApplicationCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    client_ip = request.client.host
    
    # Clean old entries
    usage_tracker[client_ip] = [
        ts for ts in usage_tracker[client_ip]
        if datetime.now() - ts < timedelta(days=1)
    ]
    
    # Check limit
    if len(usage_tracker[client_ip]) >= MAX_REQUESTS_PER_DAY:
        raise HTTPException(
            status_code=429,
            detail=f"Daily limit of {MAX_REQUESTS_PER_DAY} CVs reached"
        )
    
    # Log usage
    usage_tracker[client_ip].append(datetime.now())
    
    # ... continue with normal processing
```

## Testing

### Local Testing
```bash
# Terminal 1: Backend
python main.py

# Terminal 2: Frontend (simple python server)
cd frontend
python -m http.server 3000

# Visit: http://localhost:3000
```

### Production Testing
```bash
# Check backend
curl http://localhost:8010/

# Check frontend
curl http://cv.yourdomain.com

# Test generation (from another machine)
# Paste a job description and verify it works
```

## Monitoring

### Check Logs
```bash
# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Backend logs (if using systemd)
sudo journalctl -u vector-cv-backend -f

# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Usage Analytics

Add simple analytics to track usage:

```python
# In main.py
@app.post("/api/applications")
async def create_job_application(...):
    # Log the generation
    print(f"CV generated: {app_data.company_name} - {app_data.job_title}")
    
    # Or store in database
    # analytics.log_generation(client_ip, company_name, job_title)
```

## Marketing Your Tool

Once deployed, share it with:

1. **LinkedIn Post:**
   - "Built an AI-powered CV generator using FastAPI, React, and OpenAI GPT-4"
   - Include demo link: cv.yourdomain.com
   - Highlight: "Generates tailored CVs in 30 seconds"

2. **GitHub README:**
   - Add live demo link
   - Screenshots of the interface
   - Feature list

3. **Portfolio:**
   - Add to monatemedia.com/portfolio
   - Explain the RAG architecture
   - Show the hybrid selection strategy

## Troubleshooting

### CORS Errors
- Check `allow_origins` in `main.py`
- Verify frontend URL matches exactly (http vs https)

### API Not Reachable
- Check firewall: `sudo ufw allow 8010`
- Verify backend is running: `curl localhost:8010`
- Check Nginx proxy config

### Slow Generation
- Monitor OpenAI API usage dashboard
- Check database query performance
- Consider caching frequent job descriptions

## Next Steps

1. Deploy basic version (Option 1)
2. Test with a few job descriptions
3. Add usage limits
4. Set up monitoring
5. Share with recruiters
6. Gather feedback and iterate

## Cost Estimation

**OpenAI API Costs:**
- GPT-4 Turbo: ~$0.01-0.03 per CV generation
- Embeddings: ~$0.0001 per generation
- **Per CV: ~$0.01-0.03**

**With 3 CVs/day limit:**
- Daily: $0.03-0.09
- Monthly: $1-3
- Very affordable for a portfolio project!

## Support

If you encounter issues:
1. Check logs first
2. Verify all services are running
3. Test each component individually
4. Review CORS and API configurations