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
# ============================================
FROM python-base as production

# Install nginx
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# 1. DELETE EVERY DEFAULT CONFIG
RUN rm -rf /etc/nginx/sites-enabled/* && \
    rm -rf /etc/nginx/sites-available/* && \
    rm -rf /etc/nginx/conf.d/*

# 2. FORCE your config into the primary location
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 3. Copy React files
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# 4. PREVENT THE 404/CSS ISSUE: Ensure the directory exists and permissions are open
RUN mkdir -p /usr/share/nginx/html/assets && \
    chmod -R 755 /usr/share/nginx/html && \
    chown -R www-data:www-data /usr/share/nginx/html

EXPOSE 8010 8501 80

CMD ["nginx", "-g", "daemon off;"]