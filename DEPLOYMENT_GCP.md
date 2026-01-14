# ☁️ Deploy CoomerDL to Google Cloud Platform (GCP)

This guide explains how to deploy CoomerDL as a "Desktop on Cloud" application using Google Cloud Run. This setup allows you to run the full desktop application in a container and access it via a web browser using VNC technology.

---

## 🏗️ Architecture

Because CoomerDL is a desktop application (built with Tkinter/CustomTkinter), it requires a display server. In the cloud, we achieve this by using:

1.  **Xvfb**: A virtual X11 display server that performs all graphical operations in memory.
2.  **Fluxbox**: A lightweight window manager to handle application windows.
3.  **x11vnc**: A VNC server to expose the display.
4.  **noVNC**: A web-based VNC client that allows you to view the display in a browser.

All of these components are packaged into a single Docker container managed by `supervisord`.

---

## 🚀 One-Click Deployment (Google Cloud Run)

### Prerequisites
1.  A Google Cloud Platform (GCP) account.
2.  GCloud CLI installed (or use Cloud Shell).

### Step 1: Enable APIs
Enable the Cloud Run and Artifact Registry APIs:
```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com
```

### Step 2: Build and Submit Container
Navigate to the root of the repository and run:

```bash
# Set your Project ID
export PROJECT_ID=$(gcloud config get-value project)

# Create a repository (if you haven't already)
gcloud artifacts repositories create coomerdl-repo --repository-format=docker \
    --location=us-central1 --description="CoomerDL Docker Repository"

# Build the image
gcloud builds submit --tag us-central1-docker.pkg.dev/$PROJECT_ID/coomerdl-repo/coomerdl:latest .
```

### Step 3: Deploy to Cloud Run
Deploy the container with 2GB RAM and 1 vCPU (minimum recommended):

```bash
gcloud run deploy coomerdl \
    --image us-central1-docker.pkg.dev/$PROJECT_ID/coomerdl-repo/coomerdl:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi
```

### Step 4: Access the App
1.  Wait for the deployment to finish. GCP will provide a **Service URL**.
2.  Open the URL in your browser.
3.  Click **Connect**.
4.  Enter the default password: `coomerdl` (or the one you configured).
5.  You should see the CoomerDL interface running!

---

## ⚙️ Configuration

You can configure the deployment by setting Environment Variables in Cloud Run:

| Variable | Default | Description |
|----------|---------|-------------|
| `VNC_PASSWORD` | `coomerdl` | Password to access the VNC session |
| `RESOLUTION` | `1280x800` | Screen resolution (WidthxHeight) |

---

## 💾 Persistence Note

**Cloud Run is stateless.** This means any files downloaded to the container's filesystem will be **LOST** when the container shuts down or scales to zero.

To save your downloads, you must configure a persistent storage solution (like Google Cloud Storage FUSE) or use an external upload script.

**Future Roadmap:** We plan to add direct Google Drive or S3 upload support within the app to handle this better.

---

## 🛠️ Troubleshooting

-   **"Connection Refused"**: Ensure port 8080 is exposed and noVNC is running. Check Cloud Run logs.
-   **Black Screen**: Wait a few seconds for the app to load. If it persists, check logs for Tkinter errors.
-   **App Crashes**: Increase memory limit to 4Gi.
