"""
Download API routes.
"""
import logging
from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from backend.api.models.schemas import (
    DownloadRequest,
    DownloadResponse,
    DownloadStatusResponse,
    DownloadStatus,
)
from backend.api.services.download_service import DownloadService
from backend.config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/start", response_model=List[DownloadResponse])
async def start_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    """
    Start one or more downloads.
    
    Args:
        request: Download request with URLs and options
        background_tasks: FastAPI background tasks
        
    Returns:
        List of download responses with task IDs
    """
    responses = []
    
    # Determine download folder
    download_folder = request.download_folder or settings.local_download_folder
    
    for url in request.urls:
        try:
            # Start download asynchronously
            task_id = await DownloadService.start_download(
                url=url,
                download_folder=download_folder,
                options=request.options,
            )
            
            responses.append(DownloadResponse(
                task_id=task_id,
                status="started",
                message=f"Download started for {url}"
            ))
            
        except Exception as e:
            logger.error(f"Failed to start download for {url}: {e}")
            responses.append(DownloadResponse(
                task_id="",
                status="error",
                message=f"Failed to start download: {str(e)}"
            ))
    
    return responses


@router.get("/status/{task_id}", response_model=DownloadStatusResponse)
async def get_download_status(task_id: str):
    """
    Get status of a specific download.
    
    Args:
        task_id: Task ID to query
        
    Returns:
        Download status information
    """
    status = DownloadService.get_download_status(task_id)
    
    if not status:
        raise HTTPException(status_code=404, detail=f"Download {task_id} not found")
    
    return DownloadStatusResponse(**status)


@router.post("/cancel/{task_id}")
async def cancel_download(task_id: str):
    """
    Cancel a download.
    
    Args:
        task_id: Task ID to cancel
        
    Returns:
        Success message
    """
    success = DownloadService.cancel_download(task_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Download {task_id} not found")
    
    return {"message": f"Download {task_id} cancelled"}


@router.get("/active")
async def get_active_downloads():
    """
    Get all active downloads.
    
    Returns:
        Dictionary of active downloads
    """
    downloads = DownloadService.get_all_downloads()
    return {
        "count": len(downloads),
        "downloads": list(downloads.values())
    }
