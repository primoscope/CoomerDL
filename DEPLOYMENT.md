# CoomerDL Web Application - Deployment Guide

This guide covers deploying CoomerDL as a modern web application to multiple cloud platforms.

## Table of Contents

- [Cloud Platform Comparison](#cloud-platform-comparison)
- [Google Cloud Platform](#google-cloud-platform-gcp)
- [Amazon Web Services](#amazon-web-services-aws)
- [Microsoft Azure](#microsoft-azure)
- [Heroku](#heroku)
- [Local Development](#local-development)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Cost Estimates](#cost-estimates)

---

## Cloud Platform Comparison

Choose the platform that best fits your needs:

| Feature | Google Cloud | AWS | Azure | Heroku |
|---------|-------------|-----|-------|--------|
| **Ease of Setup** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Cost (Light Use)** | $5-10/mo | $10-15/mo | $10-15/mo | Free-$7/mo |
| **Scalability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Free Tier** | Generous | Limited | Generous | Limited |
| **Auto-scaling** | ✅ | ✅ | ✅ | ✅ |
| **Container Support** | Cloud Run | ECS Fargate | Container Apps | Dynos |
| **Storage** | Cloud Storage | S3 | Blob Storage | Add-ons |
| **Database** | Cloud SQL | RDS | Azure SQL | Add-ons |
| **Global CDN** | Yes | CloudFront | Front Door | No (add-on) |
| **Monitoring** | Cloud Monitoring | CloudWatch | Monitor | Basic |
| **Deployment Time** | 5-10 min | 10-15 min | 10-15 min | 2-5 min |

### Recommendation by Use Case

- **Hobby/Testing**: Heroku (easiest, free tier)
- **Production (Small)**: Google Cloud Run (best free tier, simple)
- **Production (Large)**: AWS ECS or Azure Container Apps (mature ecosystem)
- **Enterprise**: AWS or Azure (compliance, advanced features)

---

## Google Cloud Platform (GCP)

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

## Amazon Web Services (AWS)

Deploy CoomerDL to AWS ECS Fargate for production-grade container orchestration.

### Prerequisites

1. **AWS CLI** - [Installation Guide](https://aws.amazon.com/cli/)
   ```bash
   # Verify installation
   aws --version
   
   # Configure credentials
   aws configure
   ```

2. **Docker** - Required for building images
   ```bash
   docker --version
   ```

### Quick Start - Automated Deployment

```bash
# Clone the repository
git clone https://github.com/primoscope/CoomerDL.git
cd CoomerDL

# Set environment variables (optional)
export PROJECT_NAME=coomerdl
export ENVIRONMENT=production
export AWS_REGION=us-east-1

# Run the deployment script
./scripts/deploy-aws.sh
```

The script will:
1. ✅ Create ECR repository for Docker images
2. 🐳 Build and push Docker image to ECR
3. ☁️ Deploy CloudFormation stack with:
   - VPC with public subnets
   - Application Load Balancer
   - ECS Fargate cluster and service
   - S3 bucket for downloads
   - CloudWatch logs
   - IAM roles and security groups
4. 🌐 Provide your application URL

**Deployment time:** ~10-15 minutes

### Manual Deployment

1. **Create ECR Repository**
   ```bash
   aws ecr create-repository --repository-name coomerdl
   ```

2. **Build and Push Image**
   ```bash
   # Login to ECR
   aws ecr get-login-password --region us-east-1 | \
     docker login --username AWS --password-stdin \
     <account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   # Build and push
   docker build -t coomerdl:latest -f Dockerfile.webapp .
   docker tag coomerdl:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/coomerdl:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/coomerdl:latest
   ```

3. **Deploy CloudFormation Stack**
   ```bash
   aws cloudformation deploy \
     --template-file aws/cloudformation.yaml \
     --stack-name coomerdl-production \
     --parameter-overrides \
       ProjectName=coomerdl \
       EnvironmentName=production \
       ContainerImage=<account-id>.dkr.ecr.us-east-1.amazonaws.com/coomerdl:latest \
     --capabilities CAPABILITY_NAMED_IAM
   ```

4. **Get Application URL**
   ```bash
   aws cloudformation describe-stacks \
     --stack-name coomerdl-production \
     --query 'Stacks[0].Outputs[?OutputKey==`ApplicationURL`].OutputValue' \
     --output text
   ```

### AWS Configuration

The CloudFormation template includes:

- **Compute**: ECS Fargate (2 vCPU, 4GB RAM by default)
- **Networking**: VPC, subnets, load balancer, security groups
- **Storage**: S3 bucket with 30-day lifecycle policy
- **Monitoring**: CloudWatch logs and container insights
- **Security**: IAM roles with least-privilege access

### Scaling

```bash
# Update service desired count
aws ecs update-service \
  --cluster coomerdl-production-cluster \
  --service coomerdl-production-service \
  --desired-count 3
```

### Cleanup

```bash
# Delete the stack
aws cloudformation delete-stack --stack-name coomerdl-production

# Delete ECR repository
aws ecr delete-repository --repository-name coomerdl --force
```

---

## Microsoft Azure

Deploy CoomerDL to Azure Container Apps for serverless container hosting.

### Prerequisites

1. **Azure CLI** - [Installation Guide](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
   ```bash
   # Verify installation
   az --version
   
   # Login
   az login
   ```

2. **Docker** - Required for building images
   ```bash
   docker --version
   ```

### Quick Start - Automated Deployment

```bash
# Clone the repository
git clone https://github.com/primoscope/CoomerDL.git
cd CoomerDL

# Set environment variables (optional)
export PROJECT_NAME=coomerdl
export ENVIRONMENT=production
export AZURE_LOCATION=eastus

# Run the deployment script
./scripts/deploy-azure.sh
```

The script will:
1. ✅ Create resource group
2. 📦 Create Azure Container Registry (ACR)
3. 🐳 Build and push Docker image to ACR
4. ☁️ Deploy ARM template with:
   - Azure Container Apps environment
   - Container app with auto-scaling
   - Storage account with blob container
   - Log Analytics workspace
5. 🌐 Provide your application URL

**Deployment time:** ~10-15 minutes

### Manual Deployment

1. **Create Resource Group**
   ```bash
   az group create --name coomerdl-production-rg --location eastus
   ```

2. **Create Container Registry**
   ```bash
   az acr create \
     --resource-group coomerdl-production-rg \
     --name coomerdlacr \
     --sku Basic \
     --admin-enabled true
   ```

3. **Build and Push Image**
   ```bash
   # Login to ACR
   az acr login --name coomerdlacr
   
   # Build and push
   docker build -t coomerdl:latest -f Dockerfile.webapp .
   docker tag coomerdl:latest coomerdlacr.azurecr.io/coomerdl:latest
   docker push coomerdlacr.azurecr.io/coomerdl:latest
   ```

4. **Deploy ARM Template**
   ```bash
   az deployment group create \
     --resource-group coomerdl-production-rg \
     --template-file azure/azuredeploy.json \
     --parameters \
       projectName=coomerdl \
       environmentName=production \
       containerImage=coomerdlacr.azurecr.io/coomerdl:latest
   ```

5. **Get Application URL**
   ```bash
   az deployment group show \
     --resource-group coomerdl-production-rg \
     --name azuredeploy \
     --query properties.outputs.applicationUrl.value
   ```

### Azure Configuration

The ARM template includes:

- **Compute**: Azure Container Apps (2 cores, 4GB RAM by default)
- **Storage**: Azure Blob Storage with 7-day soft delete
- **Monitoring**: Log Analytics workspace
- **Security**: Managed identities, HTTPS only
- **Scaling**: HTTP-based auto-scaling (1-10 replicas)

### Scaling

```bash
# Update replica count
az containerapp update \
  --name coomerdl-production-app \
  --resource-group coomerdl-production-rg \
  --max-replicas 10
```

### Cleanup

```bash
# Delete resource group (includes all resources)
az group delete --name coomerdl-production-rg --yes
```

---

## Heroku

Deploy CoomerDL to Heroku for simple, managed hosting.

### Prerequisites

1. **Heroku CLI** - [Installation Guide](https://devcenter.heroku.com/articles/heroku-cli)
   ```bash
   # Verify installation
   heroku --version
   
   # Login
   heroku login
   ```

### Quick Start

```bash
# Clone the repository
git clone https://github.com/primoscope/CoomerDL.git
cd CoomerDL

# Create Heroku app
heroku create your-app-name

# Deploy
git push heroku main

# Open the app
heroku open
```

The `heroku.yml` file automatically configures:
- Docker build from `Dockerfile.webapp`
- Web dyno on port 8080
- Release commands for database migrations

**Deployment time:** ~2-5 minutes

### Configuration

```bash
# Set environment variables
heroku config:set STORAGE_TYPE=s3
heroku config:set DATABASE_URL=postgresql://...

# Scale dynos
heroku ps:scale web=2

# View logs
heroku logs --tail
```

### Addons

```bash
# PostgreSQL database
heroku addons:create heroku-postgresql:hobby-dev

# Redis for sessions
heroku addons:create heroku-redis:hobby-dev

# S3 storage (via addon)
heroku addons:create bucketeer:hobbyist
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
