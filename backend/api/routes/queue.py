"""
Queue API routes.
"""
import logging
from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException
from backend.api.models.schemas import (
    QueueItemSchema,
    QueueAddRequest,
    DownloadStatus,
)
from backend.api.services.queue_service import QueueService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[QueueItemSchema])
async def get_queue():
    """Get all items in the queue."""
    items = QueueService.get_all_items()
    response_items = []

    for i, item in enumerate(items):
        # Handle conversion
        response_items.append(
            QueueItemSchema(
                id=item.id,
                url=item.url,
                status=DownloadStatus(item.status.value),
                priority=item.priority.value,
                position=i,
                progress=item.progress,
                options=item.options,
                created_at=item.added_at,
                updated_at=item.added_at  # Fallback as updated_at is not tracked separately
            )
        )
    return response_items

@router.post("/add", response_model=List[QueueItemSchema])
async def add_to_queue(request: QueueAddRequest):
    """Add items to the queue."""
    added_items = []
    for url in request.urls:
        item = QueueService.add_item(
            url=url,
            options=request.options,
            priority=request.priority
        )
        added_items.append(
            QueueItemSchema(
                id=item.id,
                url=item.url,
                status=DownloadStatus(item.status.value),
                priority=item.priority.value,
                position=0,  # Will be updated on refresh
                progress=0.0,
                options=item.options,
                created_at=item.added_at,
                updated_at=item.added_at
            )
        )
    return added_items

@router.post("/pause/{item_id}")
async def pause_item(item_id: str):
    """Pause a queue item."""
    if QueueService.pause_item(item_id):
        return {"message": f"Item {item_id} paused"}
    raise HTTPException(status_code=404, detail="Item not found or cannot be paused")

@router.post("/resume/{item_id}")
async def resume_item(item_id: str):
    """Resume a queue item."""
    if QueueService.resume_item(item_id):
        return {"message": f"Item {item_id} resumed"}
    raise HTTPException(status_code=404, detail="Item not found or cannot be resumed")

@router.delete("/{item_id}")
async def remove_item(item_id: str):
    """Remove an item from the queue."""
    if QueueService.remove_item(item_id):
        return {"message": f"Item {item_id} removed"}
    raise HTTPException(status_code=404, detail="Item not found")

@router.post("/clear")
async def clear_completed():
    """Clear completed items from the queue."""
    count = QueueService.clear_completed()
    return {"message": f"Cleared {count} completed items"}

@router.post("/reorder/up/{item_id}")
async def move_up(item_id: str):
    """Move item up."""
    if QueueService.move_item_up(item_id):
        return {"message": "Moved up"}
    raise HTTPException(status_code=400, detail="Cannot move up")

@router.post("/reorder/down/{item_id}")
async def move_down(item_id: str):
    """Move item down."""
    if QueueService.move_item_down(item_id):
        return {"message": "Moved down"}
    raise HTTPException(status_code=400, detail="Cannot move down")
