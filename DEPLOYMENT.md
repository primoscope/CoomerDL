# CoomerDL Web Application - Deployment Guide

This guide covers deploying CoomerDL as a modern web application to Google Cloud Platform.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start - One-Click Deploy](#quick-start---one-click-deploy)
- [Manual Deployment](#manual-deployment)
- [Local Development](#local-development)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Cost Estimates](#cost-estimates)

---

## Prerequisites

### Required Tools

1. **Google Cloud SDK** - [Installation Guide](https://cloud.google.com/sdk/docs/install)
   ```bash
   # Verify installation
   gcloud --version
   ```

2. **Node.js** (v18 or higher) - [Download](https://nodejs.org/)
   ```bash
   # Verify installation
   node --version
   npm --version
   ```

3. **Docker** (optional, for local testing) - [Installation Guide](https://docs.docker.com/get-docker/)
   ```bash
   # Verify installation
   docker --version
   ```

### Google Cloud Setup

1. **Create a GCP Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select an existing one
   - Note your Project ID

2. **Enable Billing**
   - Ensure billing is enabled for your project
   - [Enable Billing](https://console.cloud.google.com/billing)

3. **Authenticate gcloud CLI**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

---

## Quick Start - One-Click Deploy

### Using the Deployment Script

The easiest way to deploy CoomerDL to Google Cloud:

```bash
# Clone the repository
git clone https://github.com/primoscope/CoomerDL.git
cd CoomerDL

# Run the deployment script
./scripts/deploy-gcp.sh
```

The script will:
1. ✅ Check prerequisites
2. 🔌 Enable required Google Cloud APIs
3. 🪣 Create a Cloud Storage bucket for downloads
4. 🎨 Build the frontend
5. 🏗️ Build and deploy to Cloud Run
6. 🌐 Provide your application URL

**Deployment time:** ~5-10 minutes

### Using Cloud Build Button

Click this button to deploy directly from GitHub:

[![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run?git_repo=https://github.com/primoscope/CoomerDL)

---

## Manual Deployment

### Step 1: Enable Required APIs

```bash
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    storage.googleapis.com
```

### Step 2: Create Storage Bucket

```bash
PROJECT_ID=$(gcloud config get-value project)
BUCKET_NAME="${PROJECT_ID}-coomerdl-downloads"

gsutil mb -l us-central1 gs://${BUCKET_NAME}
```

### Step 3: Build Frontend

```bash
cd frontend
npm ci
npm run build
cd ..
```

### Step 4: Deploy to Cloud Run

```bash
# Submit build to Cloud Build
gcloud builds submit --config cloudbuild.yaml \
    --substitutions=_GCS_BUCKET="${BUCKET_NAME}"

# Get your service URL
gcloud run services describe coomerdl \
    --region us-central1 \
    --format='value(status.url)'
```

---

## Local Development

### Using Docker Compose

The easiest way to run locally with all services:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access the application at: http://localhost:8080

### Manual Local Setup

#### 1. Backend Development

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=sqlite:///./downloads.db
export STORAGE_TYPE=local
export DOWNLOAD_FOLDER=./downloads

# Run backend
uvicorn backend.api.main:app --reload --port 8080
```

Backend will be available at: http://localhost:8080

API docs: http://localhost:8080/api/docs

#### 2. Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend will be available at: http://localhost:5173

The dev server automatically proxies API requests to the backend.

---

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Application
APP_NAME=CoomerDL
DEBUG=false
PORT=8080

# Storage
STORAGE_TYPE=gcs  # or "local" for development
GCS_BUCKET=your-bucket-name
DOWNLOAD_FOLDER=./downloads  # for local storage

# Database
DATABASE_URL=sqlite:///./downloads.db  # or PostgreSQL URL

# Security
SECRET_KEY=your-secret-key-change-this

# Redis (optional, for production)
REDIS_URL=redis://localhost:6379/0
```

### Google Cloud Environment Variables

Set via Cloud Run:

```bash
gcloud run services update coomerdl \
    --region=us-central1 \
    --set-env-vars="STORAGE_TYPE=gcs,GCS_BUCKET=your-bucket-name"
```

Or via Cloud Console:
1. Go to Cloud Run → coomerdl service
2. Click "Edit & Deploy New Revision"
3. Add environment variables in "Container" tab

---

## Troubleshooting

### Backend Won't Start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
pip install -r requirements.txt
```

### Frontend Build Fails

**Error:** `npm ERR! Missing script: "build"`

**Solution:**
```bash
cd frontend
npm install
npm run build
```

### Cloud Build Timeout

**Error:** Build exceeds 10-minute timeout

**Solution:** Increase timeout in `cloudbuild.yaml`:
```yaml
timeout: '1800s'  # 30 minutes
```

### WebSocket Connection Fails

**Error:** WebSocket connection refused

**Solution:**
1. Check that backend is running on correct port
2. Verify firewall rules allow WebSocket connections
3. Check CORS configuration in `backend/config/settings.py`

### Download Fails

**Error:** `No suitable downloader found for URL`

**Solution:**
1. Check that all dependencies are installed (beautifulsoup4, requests, etc.)
2. Verify the URL is supported
3. Check backend logs: `docker-compose logs backend`

### Cloud Run Service Unavailable

**Error:** 503 Service Unavailable

**Solution:**
1. Check service logs:
   ```bash
   gcloud logging read "resource.type=cloud_run_revision" --limit 50
   ```
2. Verify health check endpoint: `curl https://your-service-url/health`
3. Check resource limits (memory, CPU)

---

## Cost Estimates

### Google Cloud Run Pricing

Based on default configuration (2 CPU, 4GB RAM):

| Usage Level | Estimated Monthly Cost |
|-------------|----------------------|
| Light (< 100 downloads/day) | $5-10 |
| Medium (100-500 downloads/day) | $10-30 |
| Heavy (> 500 downloads/day) | $30-100+ |

**Included in costs:**
- Cloud Run compute time
- Cloud Storage (downloads)
- Network egress
- Container Registry storage

**Free tier:**
- 2 million requests/month
- 360,000 GB-seconds/month
- 180,000 vCPU-seconds/month

### Ways to Reduce Costs

1. **Enable auto-scaling down to 0**
   ```bash
   gcloud run services update coomerdl \
       --min-instances=0
   ```

2. **Use Cloud Storage lifecycle policies**
   ```bash
   # Delete files older than 30 days
   gsutil lifecycle set lifecycle.json gs://your-bucket
   ```

3. **Reduce memory allocation** (if possible)
   ```bash
   gcloud run services update coomerdl \
       --memory=2Gi
   ```

---

## Advanced Configuration

### Custom Domain

1. Go to Cloud Run → coomerdl service
2. Click "Manage Custom Domains"
3. Follow the wizard to add your domain
4. Update DNS records as instructed

### HTTPS/SSL

Cloud Run automatically provides SSL certificates for:
- Default `.run.app` domains
- Custom domains (via managed certificates)

### Authentication

To add authentication:

1. Enable Identity Platform:
   ```bash
   gcloud services enable identitytoolkit.googleapis.com
   ```

2. Update backend to require JWT tokens
3. Add authentication to frontend

### Database Migration

To use PostgreSQL instead of SQLite:

1. Create Cloud SQL instance:
   ```bash
   gcloud sql instances create coomerdl-db \
       --database-version=POSTGRES_15 \
       --tier=db-f1-micro \
       --region=us-central1
   ```

2. Update DATABASE_URL environment variable

---

## Monitoring and Logs

### View Application Logs

```bash
# Real-time logs
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=coomerdl"

# Recent logs
gcloud logging read "resource.type=cloud_run_revision" --limit 100
```

### View Metrics

Go to Cloud Console → Cloud Run → coomerdl → Metrics

Monitor:
- Request count
- Request latency
- Memory utilization
- CPU utilization
- Error rate

### Set Up Alerts

1. Go to Cloud Console → Monitoring → Alerting
2. Create policy for error rate, latency, etc.
3. Add notification channels (email, SMS, Slack)

---

## Cleanup

To completely remove the deployment:

```bash
# Delete Cloud Run service
gcloud run services delete coomerdl --region=us-central1

# Delete storage bucket
gsutil -m rm -r gs://your-bucket-name

# Delete container images
gcloud container images delete gcr.io/PROJECT_ID/coomerdl --quiet
```

---

## Support

- **GitHub Issues:** https://github.com/primoscope/CoomerDL/issues
- **Documentation:** https://github.com/primoscope/CoomerDL
- **API Docs:** https://your-service-url/api/docs

---

## Next Steps

1. ✅ Deploy your application
2. 🔐 Set up authentication (recommended)
3. 🌐 Configure custom domain (optional)
4. 📊 Set up monitoring and alerts
5. 🎨 Customize the frontend theme
6. 📚 Read the API documentation

Enjoy your cloud-native CoomerDL! 🚀
