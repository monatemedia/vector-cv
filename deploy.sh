#!/bin/bash
set -e

echo "🚀 Starting Vector CV Robust Deployment..."

# Function to build with retries
build_with_retry() {
    local service=$1
    local max_attempts=3
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        echo "📦 Building $service (Attempt $attempt/$max_attempts)..."
        # We use --no-cache only on retries to ensure we don't keep corrupted files
        if [ $attempt -eq 1 ]; then
            docker compose build "$service" && return 0
        else
            echo "⚠️ Retry detected. Cleaning up potential corrupted downloads..."
            docker compose build --no-cache "$service" && return 0
        fi
        
        echo "❌ $service build failed. Sleeping 5s before retry..."
        sleep 5
        attempt=$((attempt + 1))
    done
    return 1
}

# 1. Check .env
if [ ! -f .env ]; then echo "❌ .env missing"; exit 1; fi

# 2. Sequential Builds with Retries
build_with_retry "backend" || exit 1
build_with_retry "streamlit" || exit 1
build_with_retry "frontend" || exit 1

# 3. Bring everything up
echo "🚢 Starting containers..."
docker compose up -d

# 4. Improved Database Health Check
echo "⏳ Waiting for Database to be fully functional..."
MAX_RETRIES=30
COUNT=0
until [ $COUNT -ge $MAX_RETRIES ]; do
  # Changed 'database' to 'postgres' to match the YAML service name
  if docker compose exec postgres pg_isready -U $(grep DB_USER .env | cut -d '=' -f2) > /dev/null 2>&1; then
    echo -e "\n✅ Database is online!"
    break
  fi
  echo -n "."
  sleep 2
  COUNT=$((COUNT + 1))
done

if [ $COUNT -eq $MAX_RETRIES ]; then
  echo "❌ Database failed to start in time."
  exit 1
fi

# 5. Initialize and Seed
echo "🛠️ Initializing Database and Seeding Data..."

# ✅ Call your custom init function which handles pgvector + table creation
docker compose exec backend python -c "from database import init_db; init_db()"

# Now run the seed and verify
docker compose exec backend python seed_data.py
docker compose exec backend python verify_setup.py

echo "✅ Deployment completed successfully!"