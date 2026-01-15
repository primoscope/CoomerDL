#!/bin/bash
set -e

# CoomerDL - Heroku Deployment Script
# This script automates the deployment of CoomerDL to Heroku

echo "🚀 CoomerDL - Heroku Deployment"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check for Heroku CLI
if ! command -v heroku &> /dev/null; then
    echo -e "${RED}❌ Heroku CLI not found${NC}"
    echo "Please install from: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

echo -e "${GREEN}✓ Heroku CLI found${NC}"

# Check for Node.js and npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found${NC}"
    echo "Please install Node.js from: https://nodejs.org/"
    exit 1
fi

echo -e "${GREEN}✓ npm found${NC}"
echo ""

# Check if logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo -e "${YELLOW}Not logged in to Heroku. Please login...${NC}"
    heroku login
fi

echo -e "${GREEN}✓ Logged in to Heroku${NC}"
echo ""

# Get or create app name
echo -e "${BLUE}Enter a name for your Heroku app (leave blank to generate one):${NC}"
read -r APP_NAME

# Confirm deployment
echo ""
echo -e "${YELLOW}This will deploy CoomerDL to Heroku.${NC}"
echo "Estimated costs: ~\$7-25/month depending on dyno type and add-ons"
echo ""
echo "Deployment options:"
echo "  1. Buildpack deployment (faster, simpler)"
echo "  2. Container deployment (more control, uses Docker)"
echo ""
read -p "Choose deployment method (1 or 2): " -n 1 -r DEPLOY_METHOD
echo ""

if [[ ! $DEPLOY_METHOD =~ ^[12]$ ]]; then
    echo "Invalid choice. Defaulting to buildpack deployment."
    DEPLOY_METHOD=1
fi

echo ""

# Create Heroku app
if [ -z "$APP_NAME" ]; then
    echo "📦 Creating Heroku app with auto-generated name..."
    APP_NAME=$(heroku create --json | python3 -c "import sys, json; print(json.load(sys.stdin)['name'])")
else
    echo "📦 Creating Heroku app: $APP_NAME"
    heroku create "$APP_NAME" || {
        echo -e "${RED}❌ Failed to create app. Name may already be taken.${NC}"
        exit 1
    }
fi

echo -e "${GREEN}✓ App created: $APP_NAME${NC}"
echo ""

if [ "$DEPLOY_METHOD" -eq 2 ]; then
    # Container deployment
    echo "🐳 Setting up container deployment..."
    heroku stack:set container -a "$APP_NAME"
    echo -e "${GREEN}✓ Container stack configured${NC}"
    echo ""
else
    # Buildpack deployment
    echo "📦 Adding buildpacks..."
    heroku buildpacks:add --index 1 heroku/nodejs -a "$APP_NAME"
    heroku buildpacks:add --index 2 https://github.com/heroku/heroku-buildpack-apt -a "$APP_NAME"
    heroku buildpacks:add --index 3 heroku/python -a "$APP_NAME"
    echo -e "${GREEN}✓ Buildpacks added${NC}"
    echo ""
fi

# Add PostgreSQL database
echo "🗄️  Adding PostgreSQL database..."
heroku addons:create heroku-postgresql:essential-0 -a "$APP_NAME" || {
    echo -e "${YELLOW}⚠ Using mini plan (free tier may not be available)${NC}"
    heroku addons:create heroku-postgresql:mini -a "$APP_NAME" || {
        echo -e "${RED}❌ Failed to add database${NC}"
        exit 1
    }
}
echo -e "${GREEN}✓ Database added${NC}"
echo ""

# Configure environment variables
echo "⚙️  Setting environment variables..."
heroku config:set \
    APP_NAME=CoomerDL \
    DEBUG=false \
    STORAGE_TYPE=local \
    DOWNLOAD_FOLDER=./downloads \
    CORS_ORIGINS=* \
    PYTHONUNBUFFERED=1 \
    -a "$APP_NAME"

echo -e "${GREEN}✓ Environment variables set${NC}"
echo ""

# Build frontend
echo "🎨 Building frontend..."
cd frontend
npm ci --quiet || {
    echo -e "${RED}❌ Failed to install frontend dependencies${NC}"
    exit 1
}
npm run build || {
    echo -e "${RED}❌ Failed to build frontend${NC}"
    exit 1
}
cd ..
echo -e "${GREEN}✓ Frontend built${NC}"
echo ""

# Set up git remote if not already set
if ! git remote | grep -q heroku; then
    echo "🔗 Adding Heroku git remote..."
    heroku git:remote -a "$APP_NAME"
    echo -e "${GREEN}✓ Git remote added${NC}"
fi

# Deploy to Heroku
echo "🚀 Deploying to Heroku..."
echo "This may take 5-10 minutes..."
echo ""

git push heroku main || git push heroku master || {
    echo -e "${RED}❌ Deployment failed${NC}"
    echo "Make sure you have committed all changes and are on the main/master branch"
    exit 1
}

echo ""
echo -e "${GREEN}✅ Deployment successful!${NC}"
echo ""

# Get app URL
APP_URL=$(heroku info -a "$APP_NAME" | grep "Web URL" | awk '{print $3}')

if [ -n "$APP_URL" ]; then
    echo "🌐 Your CoomerDL instance is available at:"
    echo -e "${BLUE}$APP_URL${NC}"
    echo ""
    echo "📚 API Documentation: ${APP_URL}api/docs"
    echo ""
fi

echo "💡 Next steps:"
echo "  1. Visit your application URL above"
echo "  2. For persistent storage, set up Google Cloud Storage:"
echo "     heroku config:set STORAGE_TYPE=gcs GCS_BUCKET=your-bucket GOOGLE_CLOUD_PROJECT=your-project -a $APP_NAME"
echo "  3. Configure a custom domain (optional):"
echo "     heroku domains:add yourdomain.com -a $APP_NAME"
echo "  4. Monitor your app:"
echo "     heroku logs --tail -a $APP_NAME"
echo ""

echo "📊 Useful commands:"
echo "  View logs:        heroku logs --tail -a $APP_NAME"
echo "  View config:      heroku config -a $APP_NAME"
echo "  Scale dynos:      heroku ps:scale web=1:standard-1x -a $APP_NAME"
echo "  Open app:         heroku open -a $APP_NAME"
echo "  SSH into dyno:    heroku run bash -a $APP_NAME"
echo ""

echo "🗑️  To delete the deployment:"
echo "  heroku apps:destroy $APP_NAME"
echo ""

echo -e "${GREEN}Happy downloading! 🎉${NC}"
