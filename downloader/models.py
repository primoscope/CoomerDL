"""
Download Job and Event models for the Universal Archiver.

Provides dataclasses and enums for the unified job queue system.
All models are JSON-serializable for persistence and event transmission.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any, List


def _utc_now_iso() -> str:
    """Get current UTC time as ISO format string."""
    return datetime.now(timezone.utc).isoformat()


class JobStatus(Enum):
    """Status of a download job."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ItemStatus(Enum):
    """Status of an individual download item within a job."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class DownloadEventType(Enum):
    """Types of events emitted during download operations."""
    JOB_ADDED = "job_added"
    JOB_STARTED = "job_started"
    JOB_PROGRESS = "job_progress"
    ITEM_PROGRESS = "item_progress"
    ITEM_DONE = "item_done"
    JOB_DONE = "job_done"
    JOB_ERROR = "job_error"
    JOB_CANCELLED = "job_cancelled"
    LOG = "log"


@dataclass
class DownloadJob:
    """
    Represents a download job in the queue.
    
    A job is the unit that the UI tracks: URL + selected engine + options + status.
    """
    id: str
    url: str
    engine: str  # e.g., "Coomer", "Bunkr", "Universal (yt-dlp)", "Generic"
    status: JobStatus = JobStatus.PENDING
    created_at: str = ""  # ISO format
    started_at: Optional[str] = None  # ISO format
    finished_at: Optional[str] = None  # ISO format
    total_items: int = 0
    completed_items: int = 0
    failed_items: int = 0
    skipped_items: int = 0
    output_folder: str = ""
    error_message: Optional[str] = None
    options_snapshot: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set created_at if not provided."""
        if not self.created_at:
            self.created_at = _utc_now_iso()
    
    @classmethod
    def create(
        cls,
        url: str,
        engine: str,
        output_folder: str,
        options: Optional[Dict[str, Any]] = None
    ) -> 'DownloadJob':
        """
        Factory method to create a new job with a unique ID.
        
        Args:
            url: The URL to download from.
            engine: Name of the download engine.
            output_folder: Path to save downloaded files.
            options: Optional settings snapshot.
            
        Returns:
            New DownloadJob instance.
        """
        return cls(
            id=str(uuid.uuid4()),
            url=url,
            engine=engine,
            output_folder=output_folder,
            options_snapshot=options or {}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for serialization."""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DownloadJob':
        """Create job from dictionary."""
        data = data.copy()
        data['status'] = JobStatus(data['status'])
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert job to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'DownloadJob':
        """Create job from JSON string."""
        return cls.from_dict(json.loads(json_str))
    
    def mark_started(self) -> None:
        """Mark job as started."""
        self.status = JobStatus.RUNNING
        self.started_at = _utc_now_iso()
    
    def mark_completed(self) -> None:
        """Mark job as completed."""
        self.status = JobStatus.COMPLETED
        self.finished_at = _utc_now_iso()
    
    def mark_failed(self, error_message: str) -> None:
        """Mark job as failed."""
        self.status = JobStatus.FAILED
        self.finished_at = _utc_now_iso()
        self.error_message = error_message
    
    def mark_cancelled(self) -> None:
        """Mark job as cancelled."""
        self.status = JobStatus.CANCELLED
        self.finished_at = _utc_now_iso()
    
    def update_progress(
        self,
        total_items: int = None,
        completed_items: int = None,
        failed_items: int = None,
        skipped_items: int = None
    ) -> None:
        """Update job progress counters."""
        if total_items is not None:
            self.total_items = total_items
        if completed_items is not None:
            self.completed_items = completed_items
        if failed_items is not None:
            self.failed_items = failed_items
        if skipped_items is not None:
            self.skipped_items = skipped_items


@dataclass
class DownloadEvent:
    """
    Represents an event emitted during download operations.
    
    Events are used for:
    - UI updates (progress, status changes)
    - History logging
    - Decoupling backend from frontend
    """
    type: DownloadEventType
    job_id: str
    timestamp: str = ""  # ISO format
    payload: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = _utc_now_iso()
    
    @classmethod
    def create(
        cls,
        event_type: DownloadEventType,
        job_id: str,
        **payload
    ) -> 'DownloadEvent':
        """
        Factory method to create a new event.
        
        Args:
            event_type: Type of the event.
            job_id: ID of the associated job.
            **payload: Additional event data.
            
        Returns:
            New DownloadEvent instance.
        """
        return cls(
            type=event_type,
            job_id=job_id,
            payload=payload
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            'type': self.type.value,
            'job_id': self.job_id,
            'timestamp': self.timestamp,
            'payload': self.payload
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DownloadEvent':
        """Create event from dictionary."""
        return cls(
            type=DownloadEventType(data['type']),
            job_id=data['job_id'],
            timestamp=data['timestamp'],
            payload=data.get('payload', {})
        )
    
    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'DownloadEvent':
        """Create event from JSON string."""
        return cls.from_dict(json.loads(json_str))


# Convenience functions for creating common events

def job_added_event(job: DownloadJob) -> DownloadEvent:
    """Create a JOB_ADDED event."""
    return DownloadEvent.create(
        DownloadEventType.JOB_ADDED,
        job.id,
        url=job.url,
        engine=job.engine,
        output_folder=job.output_folder
    )


def job_started_event(job: DownloadJob) -> DownloadEvent:
    """Create a JOB_STARTED event."""
    return DownloadEvent.create(
        DownloadEventType.JOB_STARTED,
        job.id,
        url=job.url,
        engine=job.engine
    )


def job_progress_event(
    job: DownloadJob,
    completed_items: int,
    total_items: int
) -> DownloadEvent:
    """Create a JOB_PROGRESS event."""
    return DownloadEvent.create(
        DownloadEventType.JOB_PROGRESS,
        job.id,
        completed_items=completed_items,
        total_items=total_items,
        failed_items=job.failed_items,
        skipped_items=job.skipped_items
    )


def item_progress_event(
    job_id: str,
    downloaded_bytes: int,
    total_bytes: int,
    file_id: Optional[str] = None,
    file_path: Optional[str] = None,
    url: Optional[str] = None,
    speed: Optional[float] = None,
    eta: Optional[int] = None,
    status: Optional[str] = None
) -> DownloadEvent:
    """Create an ITEM_PROGRESS event."""
    payload = {
        'downloaded_bytes': downloaded_bytes,
        'total_bytes': total_bytes
    }
    if file_id:
        payload['file_id'] = file_id
    if file_path:
        payload['file_path'] = file_path
    if url:
        payload['url'] = url
    if speed is not None:
        payload['speed'] = speed
    if eta is not None:
        payload['eta'] = eta
    if status:
        payload['status'] = status
    
    return DownloadEvent.create(
        DownloadEventType.ITEM_PROGRESS,
        job_id,
        **payload
    )


def item_done_event(
    job_id: str,
    file_id: str,
    file_path: str,
    success: bool,
    error_message: Optional[str] = None
) -> DownloadEvent:
    """Create an ITEM_DONE event."""
    payload = {
        'file_id': file_id,
        'file_path': file_path,
        'success': success
    }
    if error_message:
        payload['error_message'] = error_message
    
    return DownloadEvent.create(
        DownloadEventType.ITEM_DONE,
        job_id,
        **payload
    )


def job_done_event(job: DownloadJob) -> DownloadEvent:
    """Create a JOB_DONE event."""
    return DownloadEvent.create(
        DownloadEventType.JOB_DONE,
        job.id,
        status=job.status.value,
        total_items=job.total_items,
        completed_items=job.completed_items,
        failed_items=job.failed_items,
        skipped_items=job.skipped_items
    )


def job_error_event(job: DownloadJob, error_message: str) -> DownloadEvent:
    """Create a JOB_ERROR event."""
    return DownloadEvent.create(
        DownloadEventType.JOB_ERROR,
        job.id,
        error_message=error_message
    )


def job_cancelled_event(job: DownloadJob) -> DownloadEvent:
    """Create a JOB_CANCELLED event."""
    return DownloadEvent.create(
        DownloadEventType.JOB_CANCELLED,
        job.id
    )


def log_event(job_id: str, message: str, level: str = "info") -> DownloadEvent:
    """Create a LOG event."""
    return DownloadEvent.create(
        DownloadEventType.LOG,
        job_id,
        message=message,
        level=level
    )
