"""
Main FastAPI application.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os

from backend.config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="CoomerDL Web API - Universal Media Downloader",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info(f"Starting {settings.app_name} API server")
    logger.info(f"Environment: {'DEBUG' if settings.debug else 'PRODUCTION'}")
    logger.info(f"Database: {settings.database_url}")
    logger.info(f"Storage: {settings.storage_type}")
    
    # Create download folder if using local storage
    if settings.storage_type == "local":
        os.makedirs(settings.local_download_folder, exist_ok=True)
        logger.info(f"Local download folder: {settings.local_download_folder}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down API server")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - serves frontend or info page."""
    # Check if frontend build exists
    frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend/dist/index.html")
    if os.path.exists(frontend_path):
        with open(frontend_path, 'r') as f:
            return f.read()
    
    # Fallback info page
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CoomerDL Web Application</title>
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                text-align: center; 
                padding: 50px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #fff;
                margin: 0;
            }
            .container { 
                max-width: 800px; 
                margin: 0 auto; 
                background: rgba(255, 255, 255, 0.1); 
                padding: 50px; 
                border-radius: 20px; 
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                backdrop-filter: blur(10px);
            }
            h1 { 
                font-size: 3em; 
                margin-bottom: 0.2em;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .subtitle {
                font-size: 1.3em;
                margin-bottom: 2em;
                opacity: 0.9;
            }
            a { 
                color: #fff; 
                text-decoration: none; 
                background: rgba(255,255,255,0.2);
                padding: 15px 30px;
                border-radius: 50px;
                display: inline-block;
                margin: 10px;
                transition: all 0.3s;
            }
            a:hover { 
                background: rgba(255,255,255,0.3);
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            .status {
                background: rgba(76, 175, 80, 0.3);
                padding: 10px 20px;
                border-radius: 50px;
                display: inline-block;
                margin: 20px 0;
            }
            .links {
                margin-top: 40px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 CoomerDL</h1>
            <div class="subtitle">Universal Media Downloader - Web Edition</div>
            <div class="status">✅ Backend API Running</div>
            <p>The CoomerDL backend API is running successfully!</p>
            <p>Frontend interface coming soon...</p>
            <div class="links">
                <a href="/api/docs">📚 API Documentation</a>
                <a href="https://github.com/primoscope/CoomerDL">💻 GitHub Repository</a>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "2.0.0"
    }


# Import and include routers
from backend.api.routes import downloads
from backend.api.websocket import progress

app.include_router(downloads.router, prefix="/api/downloads", tags=["downloads"])
app.include_router(progress.router, prefix="/ws", tags=["websocket"])

# Additional routers will be added in subsequent implementations
# from backend.api.routes import queue, settings, gallery, history
# app.include_router(queue.router, prefix="/api/queue", tags=["queue"])
# app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
# app.include_router(gallery.router, prefix="/api/gallery", tags=["gallery"])
# app.include_router(history.router, prefix="/api/history", tags=["history"])


# Serve static files if frontend exists
frontend_dist = os.path.join(os.path.dirname(__file__), "../../frontend/dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    logger.info("Serving frontend static assets")
