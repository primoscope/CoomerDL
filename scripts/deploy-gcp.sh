#!/bin/bash
set -e

# CoomerDL One-Click Google Cloud Platform Deployment Script
# This script automates the deployment of CoomerDL to Google Cloud Run

echo "🚀 CoomerDL - Google Cloud Platform Deployment"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check for gcloud CLI
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found${NC}"
    echo "Please install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo -e "${GREEN}✓ gcloud CLI found${NC}"

# Check for npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found${NC}"
    echo "Please install Node.js from: https://nodejs.org/"
    exit 1
fi

echo -e "${GREEN}✓ npm found${NC}"
echo ""

# Get or confirm project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}No project selected. Please enter your GCP project ID:${NC}"
    read -r PROJECT_ID
    gcloud config set project "$PROJECT_ID"
fi

echo -e "${BLUE}📦 Project ID: $PROJECT_ID${NC}"
echo ""

# Confirm deployment
echo -e "${YELLOW}This will deploy CoomerDL to Google Cloud Run.${NC}"
echo "Estimated costs: ~\$5-20/month depending on usage"
echo ""
read -p "Continue with deployment? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo "🔌 Enabling required Google Cloud APIs..."
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    storage.googleapis.com \
    sqladmin.googleapis.com \
    --project="$PROJECT_ID" \
    --quiet

echo -e "${GREEN}✓ APIs enabled${NC}"
echo ""

# Create GCS bucket for downloads
BUCKET_NAME="${PROJECT_ID}-coomerdl-downloads"
echo "🪣 Creating Cloud Storage bucket: $BUCKET_NAME"

if gsutil ls -b "gs://${BUCKET_NAME}" &> /dev/null; then
    echo -e "${YELLOW}⚠ Bucket already exists${NC}"
else
    gsutil mb -l us-central1 -p "$PROJECT_ID" "gs://${BUCKET_NAME}" || {
        echo -e "${RED}❌ Failed to create bucket${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ Bucket created${NC}"
fi
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

# Submit to Cloud Build
echo "🏗️  Building and deploying to Cloud Run..."
echo "This may take 5-10 minutes..."
echo ""

gcloud builds submit \
    --config cloudbuild.yaml \
    --substitutions=_GCS_BUCKET="$BUCKET_NAME" \
    --project="$PROJECT_ID" \
    --quiet || {
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
}

echo ""
echo -e "${GREEN}✅ Deployment successful!${NC}"
echo ""

# Get service URL
SERVICE_URL=$(gcloud run services describe coomerdl \
    --region us-central1 \
    --project="$PROJECT_ID" \
    --format='value(status.url)' 2>/dev/null)

if [ -n "$SERVICE_URL" ]; then
    echo "🌐 Your CoomerDL instance is available at:"
    echo -e "${BLUE}$SERVICE_URL${NC}"
    echo ""
    echo "📚 API Documentation: ${SERVICE_URL}/api/docs"
    echo ""
fi

echo "💡 Next steps:"
echo "  1. Visit your application URL above"
echo "  2. Configure any additional settings in GCP Console"
echo "  3. Set up a custom domain (optional)"
echo "  4. Configure authentication (recommended for production)"
echo ""

echo "📊 To view logs:"
echo "  gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=coomerdl' --limit 50 --project=$PROJECT_ID"
echo ""

echo "🗑️  To delete the deployment:"
echo "  gcloud run services delete coomerdl --region=us-central1 --project=$PROJECT_ID"
echo "  gsutil -m rm -r gs://${BUCKET_NAME}"
echo ""

echo -e "${GREEN}Happy downloading! 🎉${NC}"
