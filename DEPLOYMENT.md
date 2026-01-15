# CoomerDL Web Application - Deployment Guide

This guide covers deploying CoomerDL as a modern web application to cloud platforms.

## Table of Contents

- [Heroku Deployment](#heroku-deployment)
  - [One-Click Deploy to Heroku](#one-click-deploy-to-heroku)
  - [Manual Heroku Deployment](#manual-heroku-deployment)
  - [Container Deployment (Docker)](#container-deployment-docker)
  - [Heroku Configuration](#heroku-configuration)
- [Google Cloud Platform](#google-cloud-platform)
  - [Prerequisites](#prerequisites)
  - [Quick Start - One-Click Deploy](#quick-start---one-click-deploy)
  - [Manual Deployment](#manual-deployment)
- [Local Development](#local-development)
- [Configuration](#configuration)
- [Firebase Hosting](#firebase-hosting)
- [Troubleshooting](#troubleshooting)
- [Cost Estimates](#cost-estimates)

---

## Heroku Deployment

Deploy CoomerDL to Heroku with full functionality in minutes. Heroku provides a simple platform-as-a-service (PaaS) with easy scaling and management.

### One-Click Deploy to Heroku

The fastest way to get started - click the button below to deploy CoomerDL directly from GitHub:

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/primoscope/CoomerDL)

**What gets deployed:**
- ✅ Web application with FastAPI backend
- ✅ React frontend (pre-built)
- ✅ PostgreSQL database for download history
- ✅ FFmpeg for video processing
- ✅ All dependencies configured automatically

**Deployment time:** ~5-7 minutes

**Cost:** Starting at $7/month for basic dyno + database (see [Cost Estimates](#heroku-cost-estimates) below)

### Automated Script Deployment

Use our deployment script for a streamlined setup experience:

```bash
# Clone the repository
git clone https://github.com/primoscope/CoomerDL.git
cd CoomerDL

# Run the Heroku deployment script
./scripts/deploy-heroku.sh
```

The script will:
1. ✅ Check for Heroku CLI installation
2. 🔐 Authenticate with Heroku
3. 📦 Create a new Heroku application
4. 🗄️ Add PostgreSQL database
5. 🎨 Build the frontend
6. 🚀 Deploy the application
7. 🌐 Provide your application URL

Choose between:
- **Buildpack deployment** (option 1) - Faster, uses Heroku buildpacks
- **Container deployment** (option 2) - More control, uses Docker

### Manual Heroku Deployment

#### Prerequisites

1. **Heroku CLI** - [Installation Guide](https://devcenter.heroku.com/articles/heroku-cli)
   ```bash
   # Verify installation
   heroku --version
   ```

2. **Node.js** (v18 or higher) - [Download](https://nodejs.org/)
   ```bash
   node --version
   npm --version
   ```

3. **Git** - Required for Heroku deployments
   ```bash
   git --version
   ```

#### Step 1: Login to Heroku

```bash
heroku login
```

#### Step 2: Create Heroku Application

```bash
# Create with auto-generated name
heroku create

# Or create with custom name
heroku create your-app-name
```

#### Step 3: Add PostgreSQL Database

```bash
# Add PostgreSQL database (required for download history)
heroku addons:create heroku-postgresql:essential-0

# Or use mini plan if available
heroku addons:create heroku-postgresql:mini
```

#### Step 4: Configure Environment Variables

```bash
heroku config:set \
  APP_NAME=CoomerDL \
  DEBUG=false \
  STORAGE_TYPE=local \
  DOWNLOAD_FOLDER=./downloads \
  CORS_ORIGINS=* \
  PYTHONUNBUFFERED=1
```

**Important:** For production use, we strongly recommend using Google Cloud Storage instead of local storage:

```bash
heroku config:set \
  STORAGE_TYPE=gcs \
  GCS_BUCKET=your-bucket-name \
  GOOGLE_CLOUD_PROJECT=your-project-id
```

See [Google Cloud Storage Setup](#gcs-setup-for-heroku) below for details.

#### Step 5: Build Frontend

```bash
cd frontend
npm ci
npm run build
cd ..
```

#### Step 6: Deploy

Choose one of two deployment methods:

**Method A: Buildpack Deployment** (Recommended for most users)

```bash
# Add required buildpacks
heroku buildpacks:add --index 1 heroku/nodejs
heroku buildpacks:add --index 2 https://github.com/heroku/heroku-buildpack-apt
heroku buildpacks:add --index 3 heroku/python

# Deploy
git push heroku main
```

**Method B: Container Deployment** (Using Docker)

```bash
# Set stack to container
heroku stack:set container

# Deploy
git push heroku main
```

The container method uses the included `heroku.yml` and `Dockerfile.webapp`.

#### Step 7: Open Your Application

```bash
heroku open
```

Your CoomerDL instance is now live! 🎉

### Container Deployment (Docker)

For advanced users who want more control over the deployment environment:

#### Using heroku.yml

The repository includes a `heroku.yml` file that configures container-based deployment:

```yaml
build:
  docker:
    web: Dockerfile.webapp
run:
  web: uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT
```

#### Deploy with Container

```bash
# 1. Set stack to container
heroku stack:set container

# 2. Deploy
git push heroku main
```

Heroku will automatically:
- Build the Docker image using `Dockerfile.webapp`
- Run the web process defined in `heroku.yml`
- Handle port binding and process management

### Heroku Configuration

#### Environment Variables

View all configuration:
```bash
heroku config
```

Set individual variables:
```bash
heroku config:set VARIABLE_NAME=value
```

#### Essential Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Port number (set automatically by Heroku) | Automatic |
| `DATABASE_URL` | PostgreSQL connection (set by add-on) | Automatic |
| `SECRET_KEY` | JWT secret key | Auto-generated |
| `STORAGE_TYPE` | Storage backend: `local` or `gcs` | `local` |
| `DEBUG` | Enable debug mode | `false` |

#### GCS Setup for Heroku

For persistent storage (recommended for production), set up Google Cloud Storage:

1. **Create a GCS bucket:**
   ```bash
   # Using gcloud CLI
   gsutil mb -l us-central1 gs://your-bucket-name
   
   # Grant public read access (optional, for direct downloads)
   gsutil iam ch allUsers:objectViewer gs://your-bucket-name
   ```

2. **Create a service account:**
   ```bash
   gcloud iam service-accounts create coomerdl-heroku \
     --display-name="CoomerDL Heroku Service Account"
   
   # Grant storage permissions
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:coomerdl-heroku@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/storage.objectAdmin"
   
   # Create and download key
   gcloud iam service-accounts keys create coomerdl-key.json \
     --iam-account=coomerdl-heroku@YOUR_PROJECT_ID.iam.gserviceaccount.com
   ```

3. **Configure Heroku:**
   ```bash
   # Set storage configuration
   heroku config:set \
     STORAGE_TYPE=gcs \
     GCS_BUCKET=your-bucket-name \
     GOOGLE_CLOUD_PROJECT=your-project-id \
     GOOGLE_APPLICATION_CREDENTIALS=/app/coomerdl-key.json
   
   # Upload service account key
   # Add the key file to your repo (git-ignored for security)
   # Or use Heroku's config vars to store the JSON
   ```

#### Scaling

Scale your application based on traffic:

```bash
# Scale to multiple dynos
heroku ps:scale web=2

# Upgrade to standard dyno
heroku ps:type web=standard-1x

# Upgrade to performance dyno
heroku ps:type web=performance-m
```

#### Custom Domain

Add a custom domain to your Heroku app:

```bash
# Add domain
heroku domains:add www.yourdomain.com

# Get DNS target
heroku domains

# Add CNAME record in your DNS provider:
# www.yourdomain.com -> your-app-name.herokuapp.com
```

Heroku automatically provides SSL certificates for custom domains.

#### Monitoring

View real-time logs:
```bash
heroku logs --tail
```

View metrics in dashboard:
```bash
heroku addons:open papertrail  # If you add logging
```

### Heroku Cost Estimates

Based on typical usage patterns:

| Configuration | Monthly Cost | Details |
|--------------|--------------|---------|
| **Hobby** | ~$7 | Eco dyno ($5) + Mini Postgres ($5) - Sleeps after inactivity |
| **Basic** | ~$12 | Basic dyno ($7) + Mini Postgres ($5) - No sleeping |
| **Standard** | ~$30 | Standard-1x ($25) + Essential Postgres ($5) |
| **Production** | ~$75+ | Performance-M ($250) + Standard Postgres ($50) + Redis |

**Free tier:** Heroku no longer offers free dynos as of November 2022.

**What's included:**
- Web dyno (application server)
- PostgreSQL database (download history)
- 512MB-2.5GB RAM depending on dyno type
- Automatic SSL certificates
- Custom domain support
- Logging and metrics

**Additional costs:**
- Google Cloud Storage (if used): ~$0.01-0.10/month for typical usage
- Redis (optional): $0-15/month depending on plan
- Additional dynos for scaling: Variable

**Cost optimization tips:**
1. Use Eco dynos for development/testing (sleeps after 30min inactivity)
2. Use local storage for testing (not recommended for production)
3. Set up Google Cloud Storage for persistent files
4. Enable auto-scaling only when needed

### Heroku Troubleshooting

#### Application Crashes

```bash
# View crash logs
heroku logs --tail

# Restart application
heroku restart

# Check dyno status
heroku ps
```

#### Database Connection Issues

```bash
# View database info
heroku pg:info

# Reset database (WARNING: deletes all data)
heroku pg:reset DATABASE_URL
```

#### Build Failures

```bash
# Clear build cache
heroku repo:purge_cache -a your-app-name

# Check buildpack order
heroku buildpacks
```

#### Out of Memory

```bash
# Upgrade dyno type
heroku ps:type web=standard-2x

# Or optimize memory usage in settings
```

Common issues:
- **R14 (Memory quota exceeded)**: Upgrade dyno type or reduce concurrent downloads
- **H12 (Request timeout)**: Increase timeout or optimize download handling
- **R10 (Boot timeout)**: Build may be too large, consider container deployment

---

## Google Cloud Platform

### Prerequisites

#### Required Tools

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

#### Google Cloud Setup

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

#### Using Cloud Build Button

Click this button to deploy directly from GitHub:

[![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run?git_repo=https://github.com/primoscope/CoomerDL)

---

### Manual Deployment

#### Step 1: Enable Required APIs

```bash
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    storage.googleapis.com
```

#### Step 2: Create Storage Bucket

```bash
PROJECT_ID=$(gcloud config get-value project)
BUCKET_NAME="${PROJECT_ID}-coomerdl-downloads"

gsutil mb -l us-central1 gs://${BUCKET_NAME}
```

#### Step 3: Build Frontend

```bash
cd frontend
npm ci
npm run build
cd ..
```

#### Step 4: Deploy to Cloud Run

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

## Firebase Hosting

You can also deploy the frontend to Firebase Hosting for CDN-backed static asset delivery.

### 1. Install Firebase CLI
```bash
npm install -g firebase-tools
firebase login
firebase init hosting
```

### 2. Configure firebase.json
The `firebase.json` file controls how your app is hosted.

```json
{
  "hosting": {
    "public": "frontend/dist",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
```

**Key Settings:**
- `"public": "frontend/dist"` - Points to the Vite build output directory
- `"rewrites": [...]` - Directs all traffic to index.html (required for React Router SPA)

### 3. Deploy
```bash
# Build the frontend first
cd frontend
npm run build
cd ..

# Deploy to Firebase
firebase deploy --only hosting
```

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
