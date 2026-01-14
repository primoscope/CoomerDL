# ☁️ Deploy CoomerDL to Google Cloud Platform (GCP)

This guide explains how to deploy CoomerDL as a "Desktop on Cloud" application using Google Cloud Run. This setup allows you to run the full desktop application in a container and access it via a web browser using VNC technology.

---

## 🏗️ Architecture

Because CoomerDL is a desktop application (built with Tkinter/CustomTkinter), it requires a display server. In the cloud, we achieve this by using:

1.  **Xvfb**: A virtual X11 display server that performs all graphical operations in memory.
2.  **Fluxbox**: A lightweight window manager to handle application windows.
3.  **x11vnc**: A VNC server to expose the display.
4.  **noVNC**: A web-based VNC client that allows you to view the display in a browser.
5.  **Supervisor**: Process manager to run all services concurrently.

All of these components are packaged into a single Docker container managed by `supervisord`.

---

## 🧪 Local Testing (Recommended First Step)

Before deploying to Cloud Run, test the container locally to ensure everything works:

### Build the Docker Image
```bash
docker build -t coomerdl:latest .
```

### Run Locally
```bash
docker run -d --name coomerdl \
  -p 8080:8080 \
  -p 5900:5900 \
  -e VNC_PASSWORD=mypassword \
  coomerdl:latest
```

### Access the Application
1. Open your browser and navigate to: `http://localhost:8080/vnc.html`
2. Click **Connect**
3. Enter your VNC password (default: `coomerdl` or what you set)
4. You should see the CoomerDL desktop interface!

### Check Container Health
```bash
# View logs
docker logs -f coomerdl

# Check running processes
docker exec coomerdl ps aux

# Test health check
docker exec coomerdl curl -f http://localhost:8080/vnc.html && echo "✓ Healthy"
```

### Stop Local Container
```bash
docker stop coomerdl && docker rm coomerdl
```

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
Deploy the container with recommended settings for GUI applications:

```bash
gcloud run deploy coomerdl \
    --image us-central1-docker.pkg.dev/$PROJECT_ID/coomerdl-repo/coomerdl:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 1 \
    --timeout 3600 \
    --concurrency 1 \
    --max-instances 10 \
    --set-env-vars="VNC_PASSWORD=your-secure-password-here"
```

**Important Settings Explained:**
- `--memory 2Gi`: Minimum for GUI app (4Gi recommended for better performance)
- `--cpu 1`: One vCPU should be sufficient
- `--timeout 3600`: Max timeout (1 hour) to keep session alive
- `--concurrency 1`: One user per instance (GUI apps aren't multi-user)
- `--max-instances 10`: Limit concurrent instances for cost control
- `--set-env-vars`: Override the default VNC password for security

### Step 4: Access the App
1.  Wait for the deployment to finish. GCP will provide a **Service URL**.
2.  Open the URL in your browser (e.g., `https://coomerdl-xxxxx-uc.a.run.app/vnc.html`)
3.  Click **Connect**.
4.  Enter your VNC password (the one you set in `--set-env-vars`).
5.  You should see the CoomerDL interface running!

---

## ⚙️ Configuration

You can configure the deployment by setting Environment Variables in Cloud Run:

| Variable | Default | Description |
|----------|---------|-------------|
| `VNC_PASSWORD` | `coomerdl` | Password to access the VNC session (⚠️ **Change this for production!**) |
| `RESOLUTION` | `1280x800x24` | Screen resolution (WidthxHeightxDepth) |
| `PORT` | `8080` | HTTP port (automatically set by Cloud Run) |

### Setting Environment Variables

During deployment:
```bash
gcloud run deploy coomerdl \
    ... \
    --set-env-vars="VNC_PASSWORD=my-secure-password,RESOLUTION=1920x1080x24"
```

After deployment:
```bash
gcloud run services update coomerdl \
    --region us-central1 \
    --set-env-vars="VNC_PASSWORD=new-password"
```

---

## 💾 Persistence Note

**Cloud Run is stateless.** This means any files downloaded to the container's filesystem will be **LOST** when the container shuts down or scales to zero.

To save your downloads, you must configure a persistent storage solution (like Google Cloud Storage FUSE) or use an external upload script.

**Future Roadmap:** We plan to add direct Google Drive or S3 upload support within the app to handle this better.

---

## 🛠️ Troubleshooting

### "Connection Refused" or Cannot Access noVNC
**Symptoms**: Browser shows connection error or timeout

**Solutions**:
1. **Check if service is running:**
   ```bash
   gcloud run services describe coomerdl --region us-central1
   ```

2. **View logs for errors:**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=coomerdl" \
       --limit 100 \
       --format="table(timestamp,jsonPayload.message)"
   ```

3. **Verify health check:**
   - The container has a built-in health check
   - If services fail to start within 60 seconds, Cloud Run will restart the container

4. **Check port configuration:**
   - Ensure PORT environment variable matches the exposed port (8080)
   - Cloud Run automatically sets PORT, but you can override it

### Black Screen or No Display
**Symptoms**: noVNC connects but shows a black or frozen screen

**Solutions**:
1. **Wait 10-15 seconds** - The GUI takes time to initialize
2. **Check app logs** to see if Python application started:
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=coomerdl AND jsonPayload.message=~'main.py'" \
       --limit 50
   ```

3. **Try pressing keys or moving mouse** - Sometimes the screen needs input to refresh
4. **Increase memory** - GUI apps need resources:
   ```bash
   gcloud run services update coomerdl \
       --region us-central1 \
       --memory 4Gi
   ```

### App Crashes or Restarts Frequently
**Symptoms**: Container keeps restarting, logs show crashes

**Solutions**:
1. **Increase memory allocation:**
   ```bash
   gcloud run services update coomerdl \
       --region us-central1 \
       --memory 4Gi
   ```

2. **Check for Python errors in logs:**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" \
       --limit 50
   ```

3. **Verify all dependencies are installed** - Rebuild the image if needed

### Slow Performance
**Symptoms**: Laggy interface, slow response

**Solutions**:
1. **Increase CPU allocation:**
   ```bash
   gcloud run services update coomerdl \
       --region us-central1 \
       --cpu 2
   ```

2. **Use a closer region** to reduce latency
3. **Lower the resolution:**
   ```bash
   gcloud run services update coomerdl \
       --region us-central1 \
       --set-env-vars="RESOLUTION=1024x768x24"
   ```

### VNC Password Not Working
**Symptoms**: VNC rejects the password

**Solutions**:
1. **Check environment variable is set:**
   ```bash
   gcloud run services describe coomerdl \
       --region us-central1 \
       --format="value(spec.template.spec.containers[0].env)"
   ```

2. **Update VNC password:**
   ```bash
   gcloud run services update coomerdl \
       --region us-central1 \
       --set-env-vars="VNC_PASSWORD=new-password"
   ```

3. **Try default password** - If you haven't set a custom one, use: `coomerdl`

### Timeout Errors
**Symptoms**: "Request timeout" after 5 minutes

**Solutions**:
1. **Increase timeout to maximum:**
   ```bash
   gcloud run services update coomerdl \
       --region us-central1 \
       --timeout 3600
   ```
   
2. **Keep the session active** - Move the mouse occasionally to prevent idle timeout

### Debugging Container Locally
If Cloud Run deployment fails, test locally first:

```bash
# Build and run
docker build -t coomerdl:debug .
docker run -it --rm -p 8080:8080 coomerdl:debug

# Check logs in real-time
docker logs -f <container-id>

# Execute commands inside container
docker exec -it <container-id> bash
```

### Getting Support
If issues persist:
1. **Check GitHub Issues**: [CoomerDL Issues](https://github.com/primoscope/CoomerDL/issues)
2. **Provide logs** when reporting issues:
   ```bash
   docker logs <container-id> > coomerdl-logs.txt
   ```
3. **Include your configuration** (without passwords!)

---

## 🚀 Performance Optimization

### Recommended Settings for Different Use Cases

#### **Light Usage** (Testing, Demo):
```bash
--memory 2Gi --cpu 1 --timeout 900 --max-instances 2
```
**Cost**: ~$0.03 per active hour

#### **Standard Usage** (Regular use, smooth performance):
```bash
--memory 4Gi --cpu 2 --timeout 1800 --max-instances 5
```
**Cost**: ~$0.12 per active hour

#### **Heavy Usage** (Multiple apps, large downloads):
```bash
--memory 8Gi --cpu 4 --timeout 3600 --max-instances 10
```
**Cost**: ~$0.48 per active hour

### Performance Tips
1. **Use minimum concurrency**: Set `--concurrency 1` for single-user GUI
2. **Warm instances**: Set `--min-instances 1` if you need instant access (costs more)
3. **Choose nearby region**: Reduces latency significantly
4. **Optimize resolution**: Lower resolution = better performance
5. **Close unused apps**: Within CoomerDL, close downloaders when done

---

## 💰 Cost Considerations

**Cloud Run Pricing** (us-central1 region, approximate as of January 2024):
- CPU: $0.00002400 per vCPU-second
- Memory: $0.00000250 per GiB-second
- Requests: $0.40 per million

**Example Costs**:
- **1 hour session (2Gi RAM, 1 vCPU)**: ~$0.03
- **10 hours/month (4Gi RAM, 2 vCPU)**: ~$1.20
- **Always-on (min-instance=1)**: ~$50-100/month

**Cost Saving Tips**:
1. **No min-instances**: Let Cloud Run scale to zero when not in use
2. **Set max-instances**: Prevent unexpected scaling costs
3. **Use --timeout wisely**: Auto-terminate idle sessions
4. **Monitor usage**: Use GCP billing dashboard
5. **Delete when not needed**: `gcloud run services delete coomerdl`

---

## 🔐 Security Best Practices

1. **Change Default VNC Password**:
   ```bash
   --set-env-vars="VNC_PASSWORD=$(openssl rand -base64 12)"
   ```

2. **Require Authentication**: Remove `--allow-unauthenticated` and use Cloud IAM:
   ```bash
   gcloud run deploy coomerdl \
       --no-allow-unauthenticated \
       ...
   ```

3. **Use Private VPC**: For production, deploy in a private network

4. **Regular Updates**: Rebuild image periodically to get security patches

5. **Firewall Rules**: Limit access by IP if possible

---
