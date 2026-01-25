#!/bin/bash
set -euo pipefail

echo "🚀 Starting Vector CV Production Deployment..."

# Environment variables passed from GitHub Actions
DEPLOY_TAG="production"
FULL_IMAGE_NAME="${IMAGE_NAME}:${DEPLOY_TAG}"

echo "--- Deployment Configuration ---"
echo "📦 Image: ${FULL_IMAGE_NAME}"
echo "🌐 Domain: ${VIRTUAL_HOST}"
echo "📂 Work Directory: $(pwd)"

# -------------------------------------------------------------
# 1. PULL THE LATEST IMAGE
# -------------------------------------------------------------
echo "📥 Pulling latest image: ${FULL_IMAGE_NAME}"
docker pull ${FULL_IMAGE_NAME}

export IMAGE_TAG=${DEPLOY_TAG}
echo "🏷️ Exported IMAGE_TAG=${IMAGE_TAG}"

# -------------------------------------------------------------
# 2. STOP EXISTING CONTAINERS
# -------------------------------------------------------------
echo "🛑 Stopping existing containers..."
docker compose down || true

# -------------------------------------------------------------
# 3. ENSURE PROXY NETWORK EXISTS
# -------------------------------------------------------------
echo "🌐 Ensuring proxy-network exists..."
docker network create proxy-network 2>/dev/null || echo "proxy-network already exists"

# -------------------------------------------------------------
# 4. START DATABASE FIRST
# -------------------------------------------------------------
echo "🗄️ Starting PostgreSQL database..."
docker compose up -d postgres

# -------------------------------------------------------------
# 5. WAIT FOR DATABASE TO BE READY
# -------------------------------------------------------------
echo "⏳ Waiting for database to be ready..."
MAX_RETRIES=30
COUNT=0

# Load database credentials safely
RAW_DB_USER=$(grep "^DB_USER=" .env | cut -d '=' -f 2- | tr -d '\r' | xargs || echo "vector_cv_user")
RAW_DB_NAME=$(grep "^DB_DATABASE=" .env | cut -d '=' -f 2- | tr -d '\r' | xargs || echo "vector_cv_db")
RAW_DB_PASS=$(grep "^DB_PASSWORD=" .env | cut -d '=' -f 2- | tr -d '\r' | xargs || echo "")

export DB_USER="${RAW_DB_USER}"
export DB_NAME="${RAW_DB_NAME}"
export DB_PASSWORD="${RAW_DB_PASS}"

until docker compose exec -T postgres pg_isready -U "${DB_USER}" -d "${DB_NAME}" > /dev/null 2>&1; do
    COUNT=$((COUNT + 1))
    if [ $COUNT -ge $MAX_RETRIES ]; then
        echo "❌ Error: Database was not ready after 60 seconds."
        exit 1
    fi
    echo "Still waiting for DB... ($COUNT/$MAX_RETRIES)"
    sleep 2
done

echo "✅ Database is ready."

# -------------------------------------------------------------
# 6. INITIALIZE DATABASE
# -------------------------------------------------------------
echo "🛠️ Initializing database schema and seeding data..."

# Run database initialization
docker compose run --rm -T backend python -c "from database import init_db; init_db()"

if [ $? -eq 0 ]; then
    echo "✅ Database initialized successfully."
    
    # Run seeding
    echo "🌱 Seeding database..."
    docker compose run --rm -T backend python seed_data.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Database seeded successfully."
    else
        echo "⚠️ Warning: Database seeding failed. Check logs."
    fi
    
    # Verify setup
    echo "🔍 Verifying setup..."
    docker compose run --rm -T backend python verify_setup.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Setup verification passed."
    else
        echo "⚠️ Warning: Setup verification failed. Check logs."
    fi
else
    echo "❌ Database initialization failed!"
    exit 1
fi

# -------------------------------------------------------------
# 7. START ALL SERVICES
# -------------------------------------------------------------
echo "🚢 Starting all services..."
docker compose up -d

# -------------------------------------------------------------
# 8. WAIT FOR SERVICES TO BE HEALTHY
# -------------------------------------------------------------
echo "⏳ Waiting for services to be healthy..."
sleep 15

# -------------------------------------------------------------
# 9. CHECK SERVICE STATUS
# -------------------------------------------------------------
echo "📊 Checking service status..."
docker compose ps

# Check if backend is responding
echo "🔍 Checking backend health..."
BACKEND_HEALTH=$(docker compose exec -T backend curl -s -o /dev/null -w "%{http_code}" http://localhost:8010/docs || echo "000")

if [ "$BACKEND_HEALTH" = "200" ]; then
    echo "✅ Backend is healthy (HTTP $BACKEND_HEALTH)"
else
    echo "⚠️ Warning: Backend health check returned HTTP $BACKEND_HEALTH"
fi

# Check if admin is responding
echo "🔍 Checking admin health..."
ADMIN_HEALTH=$(docker compose exec -T admin curl -s -o /dev/null -w "%{http_code}" http://localhost:8501/admin || echo "000")

if [ "$ADMIN_HEALTH" = "200" ]; then
    echo "✅ Admin is healthy (HTTP $ADMIN_HEALTH)"
else
    echo "⚠️ Warning: Admin health check returned HTTP $ADMIN_HEALTH"
fi

echo "✅ Deployment completed successfully!"
echo "--- Vector CV Deployment Finished ---"
echo ""
echo "🌐 Application URLs:"
echo "   • Frontend: https://${VIRTUAL_HOST}"
echo "   • Admin: https://${VIRTUAL_HOST}/admin"
echo "   • API Docs: https://${VIRTUAL_HOST}/docs"