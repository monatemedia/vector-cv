# ============================================
# Multi-stage Dockerfile for Vector CV
# Single build, multiple target stages
# ============================================

# ============================================
# Stage 1: Python Base
# ============================================
FROM python:3.12-slim as python-base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python application code
COPY *.py ./
COPY my_data/ ./my_data/

# Create directories
RUN mkdir -p generated_docs

# ============================================
# Stage 2: Frontend Builder (Node.js)
# ============================================
FROM node:22-slim as frontend-builder

WORKDIR /app

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --legacy-peer-deps

# Copy frontend source
COPY frontend/ .

# Build environment variables for Vite
ARG VITE_API_URL=https://edward.monatemedia.com
ENV VITE_API_URL=$VITE_API_URL

# Build the React app
RUN npm run build

# ============================================
# Final Stage: Production Image
# This single image contains all services
# The docker-compose.yml determines which command runs
# ============================================
FROM python-base as production

# Install nginx for frontend serving
RUN apt-get update && apt-get install -y \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN rm /etc/nginx/sites-enabled/default || true

# Copy built React app from builder stage
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# Ensure nginx can read the frontend files
RUN chmod -R 755 /usr/share/nginx/html

# Expose all ports (compose will map them)
EXPOSE 8010 8501 80

# Default command (will be overridden by docker-compose)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010"]