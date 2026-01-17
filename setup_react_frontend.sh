#!/bin/bash

# Vector CV React Frontend Setup Script
# This script sets up the public-facing React application

set -e  # Exit on error

echo "================================================"
echo "Vector CV - React Frontend Setup"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get current directory
PROJECT_DIR=$(pwd)

echo -e "${BLUE}📁 Project directory: $PROJECT_DIR${NC}"
echo ""

# Step 1: Create frontend directory
echo -e "${BLUE}Step 1: Creating frontend directory...${NC}"
mkdir -p frontend
cd frontend

# Step 2: Create index.html
echo -e "${BLUE}Step 2: Creating index.html...${NC}"
cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Vector CV - AI-Powered Resume Synthesizer</title>
  <meta name="description" content="Generate perfectly tailored CVs and cover letters in seconds using AI. Built by Edward Baitsewe.">
  
  <!-- Favicon -->
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>✨</text></svg>">
  
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  
  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  
  <style>
    body {
      font-family: 'Inter', sans-serif;
    }
    
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
    
    .animate-pulse {
      animation: pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    html {
      scroll-behavior: smooth;
    }
  </style>
</head>
<body>
  <div id="root"></div>
  
  <script type="module">
    // React app will be loaded here via CDN
    // This is a placeholder - the full React code will be injected by the artifact
    document.getElementById('root').innerHTML = `
      <div style="display: flex; align-items: center; justify-content: center; min-height: 100vh; background: linear-gradient(to bottom right, #1e293b, #581c87, #1e293b);">
        <div style="text-align: center; color: white;">
          <h1 style="font-size: 3rem; font-weight: bold; margin-bottom: 1rem;">Vector CV</h1>
          <p style="font-size: 1.5rem; color: #c084fc;">Loading...</p>
        </div>
      </div>
    `;
  </script>
</body>
</html>
EOF

echo -e "${GREEN}✅ index.html created${NC}"

# Step 3: Create README
echo -e "${BLUE}Step 3: Creating README...${NC}"
cat > README.md << 'EOF'
# Vector CV - React Frontend

## Overview
This is the public-facing interface for the Vector CV application. It allows recruiters and other users to generate tailored CVs and cover letters.

## Files
- `index.html` - Main application file (single-page app)
- `nginx.conf` - Nginx configuration for production

## Local Development

### Option 1: Python SimpleHTTPServer
```bash
python -m http.server 3000
```

Then visit: http://localhost:3000

### Option 2: Node.js http-server
```bash
npx http-server -p 3000
```

## Production Deployment

### Option 1: Direct Nginx
Place files in `/var/www/vector-cv/` and configure Nginx to serve them.

### Option 2: Docker
```bash
docker build -t vector-cv-frontend .
docker run -p 3000:80 vector-cv-frontend
```

## API Configuration
The app connects to the FastAPI backend at port 8010. Make sure:
1. Backend is running
2. CORS is configured correctly
3. Rate limiting is enabled if needed

## Environment Variables
Set these in your .env file:
- `MAX_CV_PER_DAY=3` - Rate limit for public users
- `ENABLE_RATE_LIMITING=true` - Enable/disable rate limiting

## Security
- Rate limiting: 3 CVs per IP per day (configurable)
- No authentication required (public tool)
- Backend validates all requests

## Support
For issues, contact: edward@monatemedia.com
EOF

echo -e "${GREEN}✅ README.md created${NC}"

# Step 4: Create nginx config
echo -e "${BLUE}Step 4: Creating nginx.conf...${NC}"
cat > nginx.conf << 'EOF'
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Main app
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache";
    }

    # API proxy (for Docker setup)
    location /api/ {
        proxy_pass http://backend:8010/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
EOF

echo -e "${GREEN}✅ nginx.conf created${NC}"

# Step 5: Create Dockerfile
echo -e "${BLUE}Step 5: Creating Dockerfile...${NC}"
cat > Dockerfile << 'EOF'
FROM nginx:alpine

# Copy static files
COPY index.html /usr/share/nginx/html/

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
EOF

echo -e "${GREEN}✅ Dockerfile created${NC}"

# Step 6: Update .env file
echo -e "${BLUE}Step 6: Updating .env configuration...${NC}"
cd "$PROJECT_DIR"

if [ -f .env ]; then
    # Check if rate limiting vars exist
    if ! grep -q "ENABLE_RATE_LIMITING" .env; then
        echo "" >> .env
        echo "# Rate Limiting for Public Frontend" >> .env
        echo "ENABLE_RATE_LIMITING=true" >> .env
        echo "MAX_CV_PER_DAY=3" >> .env
        echo -e "${GREEN}✅ Added rate limiting configuration to .env${NC}"
    else
        echo -e "${YELLOW}⚠️  Rate limiting already configured in .env${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No .env file found. Please create one manually.${NC}"
fi

# Step 7: Test local setup
echo ""
echo -e "${BLUE}Step 7: Testing setup...${NC}"
cd "$PROJECT_DIR/frontend"

echo -e "${YELLOW}Starting local test server on port 3000...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "================================================"
echo "Next Steps:"
echo "================================================"
echo "1. Make sure your FastAPI backend is running:"
echo "   $ python main.py"
echo ""
echo "2. Test the frontend locally:"
echo "   $ cd frontend"
echo "   $ python -m http.server 3000"
echo ""
echo "3. Visit http://localhost:3000 in your browser"
echo ""
echo "4. For production deployment, see:"
echo "   frontend/README.md"
echo "================================================"
echo ""

# Ask if user wants to start test server
read -p "Start local test server now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}Starting server...${NC}"
    python -m http.server 3000
fi
EOF

echo -e "${GREEN}✅ Setup script created${NC}"
echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "To use this script:"
echo "1. chmod +x setup_react_frontend.sh"
echo "2. ./setup_react_frontend.sh"
echo ""