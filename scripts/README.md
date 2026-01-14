# CoomerDL Scripts

Utility scripts for development, testing, and deployment.

## Available Scripts

### `deploy-gcp.sh`

One-click deployment script for Google Cloud Platform.

**Usage:**
```bash
./scripts/deploy-gcp.sh
```

**What it does:**
- ✅ Checks prerequisites (gcloud, npm)
- 🔌 Enables required GCP APIs
- 🪣 Creates Cloud Storage bucket
- 🎨 Builds frontend
- 🏗️ Deploys to Cloud Run
- 🌐 Provides service URL

**Requirements:**
- Google Cloud SDK (gcloud)
- Node.js and npm
- Active GCP project with billing enabled

---

### `test-webapp.sh`

Comprehensive test suite for the web application.

**Usage:**
```bash
./scripts/test-webapp.sh
```

**Tests:**
- Python version and dependencies
- Backend structure and imports
- Frontend structure
- Docker configuration
- Deployment files
- API health check

**Exit Codes:**
- `0` - All tests passed
- `1` - One or more tests failed

---

## Development Scripts

### Quick Start Backend

```bash
# From project root
pip install -r requirements.txt
python -m uvicorn backend.api.main:app --reload --port 8080
```

### Quick Start Frontend

```bash
cd frontend
npm install
npm run dev
```

### Quick Start Full Stack (Docker)

```bash
docker-compose up -d
```

---

## Troubleshooting

### Script Permission Denied

If you get a permission denied error:

```bash
chmod +x scripts/*.sh
```

### gcloud Not Found

Install Google Cloud SDK:
- https://cloud.google.com/sdk/docs/install

### npm Not Found

Install Node.js:
- https://nodejs.org/

---

## Contributing

When adding new scripts:

1. Use bash shebang: `#!/bin/bash`
2. Add descriptive comments
3. Include error handling
4. Make executable: `chmod +x script.sh`
5. Update this README
6. Test thoroughly before committing
