#!/bin/bash
set -euo pipefail

echo "🚀 Starting Vector CV Production Deployment..."

# 1. PULL THE LATEST IMAGE
echo "📥 Pulling latest image: ${IMAGE_NAME}:production"
docker pull ${IMAGE_NAME}:production

# 2. STOP AND RESTART (Laravel Style - No -v flag!)
echo "🛑 Restarting containers..."
docker compose down
docker compose up -d postgres

# 3. WAIT FOR DATABASE (Fixed Grep Logic)
echo "⏳ Waiting for database to be ready..."
MAX_RETRIES=30
COUNT=0

# Extract values from .env (using the correct keys from your docker-compose)
DB_USER=$(grep "^DB_USER=" .env | cut -d '=' -f 2- | tr -d '\r')
DB_NAME=$(grep "^DB_NAME=" .env | cut -d '=' -f 2- | tr -d '\r')

until docker compose exec -T postgres \
    psql -U "${DB_USER}" -d "${DB_NAME}" -c "SELECT 1" -d "${DB_NAME}" > /dev/null 2>&1; do
    COUNT=$((COUNT + 1))
    if [ $COUNT -ge $MAX_RETRIES ]; then
        echo "❌ Error: Database was not ready after 60 seconds."
        exit 1
    fi
    echo "Still waiting for DB... ($COUNT/$MAX_RETRIES)"
    sleep 2
done
echo "✅ Database is ready."

# 4. INITIALIZE DATABASE
echo "🛠️ Initializing database schema..."
# We use 'docker compose run' and pass the .env file explicitly
docker compose run --rm -T backend python -c "from database import init_db; init_db()"

# 5. START REMAINING SERVICES
echo "🚢 Starting all services..."
docker compose up -d

echo "✅ Deployment completed successfully!"