"""
Pydantic models for API request/response schemas.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class DownloadStatus(str, Enum):
    """Download status enum."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class DownloadOptionsSchema(BaseModel):
    """Download options schema."""
    download_images: bool = True
    download_videos: bool = True
    download_compressed: bool = True
    download_documents: bool = True
    max_retries: int = 3
    retry_interval: float = 2.0
    chunk_size: int = 1048576
    timeout: int = 30
    min_file_size: int = 0
    max_file_size: int = 0
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    excluded_extensions: List[str] = Field(default_factory=list)
    proxy_type: str = 'none'
    proxy_url: str = ''
    user_agent: Optional[str] = None
    bandwidth_limit_kbps: int = 0
    connection_timeout: int = 30
    read_timeout: int = 60


class DownloadRequest(BaseModel):
    """Request to start a download."""
    urls: List[str]
    download_folder: Optional[str] = None
    options: Optional[DownloadOptionsSchema] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "urls": ["https://example.com/media"],
                "options": {
                    "download_images": True,
                    "download_videos": True
                }
            }
        }


class DownloadResponse(BaseModel):
    """Response from starting a download."""
    task_id: str
    status: str
    message: str


class DownloadStatusResponse(BaseModel):
    """Response with download status."""
    task_id: str
    status: DownloadStatus
    url: str
    progress: float = 0.0
    current_file: Optional[str] = None
    total_files: int = 0
    completed_files: int = 0
    failed_files: int = 0
    download_speed: float = 0.0
    eta_seconds: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class QueueItemSchema(BaseModel):
    """Queue item schema."""
    id: str
    url: str
    status: DownloadStatus
    priority: int = 0
    position: int = 0
    options: Optional[DownloadOptionsSchema] = None
    created_at: datetime
    updated_at: datetime


class QueueAddRequest(BaseModel):
    """Request to add items to queue."""
    urls: List[str]
    priority: int = 0
    options: Optional[DownloadOptionsSchema] = None


class QueueReorderRequest(BaseModel):
    """Request to reorder queue items."""
    item_ids: List[str]


class SettingsSchema(BaseModel):
    """User settings schema."""
    language: str = "en"
    theme: str = "dark"
    max_concurrent_downloads: int = 3
    download_folder: str = "./downloads"
    proxy_type: str = "none"
    proxy_url: str = ""
    user_agent: Optional[str] = None
    bandwidth_limit_kbps: int = 0
    log_level: str = "INFO"


class GalleryFileSchema(BaseModel):
    """Gallery file schema."""
    id: str
    filename: str
    file_type: str
    size: int
    url: str
    thumbnail_url: Optional[str] = None
    download_date: datetime


class HistoryItemSchema(BaseModel):
    """Download history item schema."""
    id: str
    url: str
    status: DownloadStatus
    total_files: int
    completed_files: int
    failed_files: int
    total_bytes: int
    elapsed_seconds: float
    created_at: datetime
    completed_at: Optional[datetime] = None


class ProgressUpdate(BaseModel):
    """WebSocket progress update."""
    task_id: str
    status: DownloadStatus
    progress: float
    current_file: Optional[str] = None
    download_speed: float = 0.0
    eta_seconds: Optional[float] = None


class LogMessage(BaseModel):
    """WebSocket log message."""
    timestamp: datetime
    level: str
    message: str
