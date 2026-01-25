# Vector CV - Quick Reference Guide

## 🚀 Deployment Commands

### Deploy to Production
```bash
# Create and push a version tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Or manually trigger via GitHub Actions
# Go to: Actions → Deploy Vector CV to Production → Run workflow
```

### Test Locally First
```bash
# Run local test
chmod +x test-local.sh
./test-local.sh

# Access locally
# Frontend: http://localhost:3000
# Admin: http://localhost:8501
# API: http://localhost:8010/docs
```

## 🔐 Setup GitHub Secrets

### Generate Secrets Helper
```bash
chmod +x setup-secrets.sh
./setup-secrets.sh
```

### Required Secrets
| Secret | Description |
|--------|-------------|
| `PAT` | GitHub Personal Access Token |
| `HOST` | VPS IP (77.243.85.71) |
| `USER` | SSH user (edward) |
| `SSH_KEY` | Private SSH key |
| `WORK_DIR` | /home/edward/vector-cv |
| `AUTH_USERNAME` | Admin username |
| `AUTH_PASSWORD` | Bcrypt hashed password |
| `AUTH_NAME` | Admin display name |
| `AUTH_EMAIL` | Admin email |
| `COOKIE_KEY` | Random secret key |
| `DB_PASSWORD` | Database password |
| `PROXY_ROOT_PATH` | API prefix (usually empty) |
| `ALLOWED_ORIGINS` | https://edward.monatemedia.com |
| `ADMIN_API_KEY` | Rate limit bypass key |
| `OPENAI_API_KEY` | OpenAI API key |

## 🔧 VPS Management

### SSH to VPS
```bash
ssh edward@77.243.85.71
cd ~/vector-cv
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f admin
docker compose logs -f frontend
docker compose logs -f postgres
```

### Check Service Status
```bash
# List running containers
docker compose ps

# Check health
docker compose exec backend curl http://localhost:8010/docs
docker compose exec admin curl http://localhost:8501
docker compose exec frontend curl http://localhost:80
```

### Restart Services
```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart backend
docker compose restart admin
docker compose restart frontend
```

### Stop/Start Services
```bash
# Stop all
docker compose down

# Start all
docker compose up -d

# Rebuild and start
docker compose up -d --build
```

### Manual Deployment
```bash
# Pull latest image
docker pull ghcr.io/YOUR_USERNAME/vector-cv:production

# Update .env with new tag
sed -i 's/IMAGE_TAG=.*/IMAGE_TAG=production/' .env

# Deploy
./deploy-prod.sh
```

## 🗄️ Database Management

### Backup Database
```bash
# Create backup
docker compose exec postgres pg_dump -U vector_cv_user vector_cv_db > backup_$(date +%Y%m%d).sql

# Compress backup
gzip backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
# Restore from backup
cat backup_20260125.sql | docker compose exec -T postgres psql -U vector_cv_user vector_cv_db

# Or from compressed
gunzip -c backup_20260125.sql.gz | docker compose exec -T postgres psql -U vector_cv_user vector_cv_db
```

### Access Database
```bash
# Via psql
docker compose exec postgres psql -U vector_cv_user -d vector_cv_db

# Common queries
# List tables: \dt
# Describe table: \d table_name
# List databases: \l
# Quit: \q
```

### Re-seed Database
```bash
docker compose run --rm backend python seed_data.py
docker compose run --rm backend python verify_setup.py
```

## 🌐 Testing Endpoints

### Frontend
```bash
curl https://edward.monatemedia.com
```

### Admin Panel
```bash
curl https://edward.monatemedia.com/admin
```

### API Documentation
```bash
curl https://edward.monatemedia.com/docs
```

### API Health Check
```bash
curl https://edward.monatemedia.com/api/health
```

### Test with Headers
```bash
curl -H "Origin: https://edward.monatemedia.com" \
     -H "Content-Type: application/json" \
     https://edward.monatemedia.com/api/endpoint
```

## 🐛 Troubleshooting

### 502 Bad Gateway
```bash
# Check backend logs
docker compose logs backend

# Restart backend
docker compose restart backend
```

### Database Connection Issues
```bash
# Check database health
docker compose exec postgres pg_isready -U vector_cv_user -d vector_cv_db

# Check database logs
docker compose logs postgres

# Restart database
docker compose restart postgres
```

### SSL Certificate Issues
```bash
# Check letsencrypt logs
docker logs letsencrypt-companion

# Verify DNS
dig edward.monatemedia.com

# Force certificate renewal (from nginx-proxy directory)
cd ~/nginx-proxy
docker compose restart letsencrypt-companion
```

### Container Won't Start
```bash
# Check logs
docker compose logs <service-name>

# Remove and recreate
docker compose down
docker compose up -d <service-name>

# Check for port conflicts
sudo netstat -tulpn | grep <port>
```

### Out of Disk Space
```bash
# Check disk usage
df -h

# Clean up Docker
docker system prune -a --volumes

# Remove old images
docker images | grep vector-cv | tail -n +4 | awk '{print $3}' | xargs docker rmi
```

## 🔄 Rollback

### Rollback to Previous Version
```bash
# SSH to VPS
ssh edward@77.243.85.71
cd ~/vector-cv

# Check available versions
docker images | grep vector-cv

# Pull specific version
docker pull ghcr.io/YOUR_USERNAME/vector-cv:v1.0.0

# Update .env
sed -i 's/IMAGE_TAG=production/IMAGE_TAG=v1.0.0/' .env

# Restart
docker compose down
docker compose up -d
```

## 📊 Monitoring

### Resource Usage
```bash
# Container stats
docker stats

# Disk usage
docker system df

# Specific container
docker stats vector-cv-backend
```

### Check Application Logs
```bash
# Last 100 lines
docker compose logs --tail=100 backend

# Follow logs
docker compose logs -f backend

# Since timestamp
docker compose logs --since 2026-01-25T10:00:00 backend
```

## 🛠️ Maintenance

### Update Dependencies
```bash
# Update Python packages (local)
pip install -U -r requirements.txt
pip freeze > requirements.txt

# Update Node packages (local)
cd frontend
npm update
npm audit fix

# Commit and deploy new version
git add requirements.txt frontend/package*.json
git commit -m "Update dependencies"
git tag -a v1.1.0 -m "Update dependencies"
git push origin v1.1.0
```

### Clean Up Logs
```bash
# Clear logs for a container
truncate -s 0 $(docker inspect --format='{{.LogPath}}' vector-cv-backend)

# Or restart with log rotation
docker compose down
docker compose up -d
```

## 🔒 Security

### Rotate Secrets
```bash
# Generate new cookie key
openssl rand -hex 32

# Generate new API key
openssl rand -hex 32

# Update in GitHub Secrets
# Then redeploy
```

### Check Open Ports
```bash
# On VPS
sudo netstat -tulpn | grep LISTEN

# Should only see:
# 22 (SSH)
# 80 (HTTP)
# 443 (HTTPS)
```

### Firewall Status
```bash
# Check UFW status
sudo ufw status

# Ensure only necessary ports are open
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 📝 File Locations

### On VPS
```
/home/edward/
├── vector-cv/              # Application directory
│   ├── .env               # Environment variables
│   ├── docker-compose.yml # Service definitions
│   ├── deploy-prod.sh     # Deployment script
│   └── generated_docs/    # Generated documents
├── nginx-proxy/           # Reverse proxy
│   └── docker-compose.yml
└── .ssh/
    └── authorized_keys    # SSH keys
```

### In Repository
```
vector-cv/
├── .github/
│   └── workflows/
│       └── deploy-production.yml
├── frontend/
│   ├── src/
│   ├── nginx.conf
│   └── package.json
├── Dockerfile
├── docker-compose.yml
├── deploy-prod.sh
├── requirements.txt
└── *.py                   # Python application files
```

## 🎯 Common Tasks

### Add New Python Dependency
```bash
# Local
pip install new-package
pip freeze > requirements.txt

# Commit and deploy
git add requirements.txt
git commit -m "Add new-package"
git tag -a v1.x.x -m "Add dependency"
git push origin v1.x.x
```

### Update Environment Variable
```bash
# Update GitHub Secret
# Go to: Settings → Secrets and variables → Actions → Update secret

# Redeploy to apply changes
git tag -a v1.x.x -m "Update config"
git push origin v1.x.x
```

### Check Application Version
```bash
# View current image tag
docker compose exec backend env | grep IMAGE_TAG

# View image info
docker inspect ghcr.io/YOUR_USERNAME/vector-cv:production
```

---

**Pro Tip**: Bookmark this file and keep it handy for quick reference during operations! 🔖