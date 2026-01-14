"""
WebSocket endpoints for real-time updates.
"""
import asyncio
import logging
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime
import json

logger = logging.getLogger(__name__)
router = APIRouter()

# Store active WebSocket connections
active_connections: Set[WebSocket] = set()


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_personal(self, message: dict, websocket: WebSocket):
        """Send a message to a specific client."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")


# Global connection manager
manager = ConnectionManager()


@router.websocket("/progress")
async def websocket_progress(websocket: WebSocket):
    """
    WebSocket endpoint for real-time progress updates.
    
    Clients can subscribe to progress updates for downloads.
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Wait for messages from client (e.g., ping/pong)
            data = await websocket.receive_text()
            
            # Echo back to confirm connection is alive
            if data == "ping":
                await websocket.send_text("pong")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected from progress WebSocket")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/logs")
async def websocket_logs(websocket: WebSocket):
    """
    WebSocket endpoint for real-time log streaming.
    
    Clients can subscribe to receive log messages in real-time.
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            
            # Handle ping/pong for keep-alive
            if data == "ping":
                await websocket.send_text("pong")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected from logs WebSocket")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def broadcast_progress_update(task_id: str, update: dict):
    """
    Broadcast a progress update to all connected clients.
    
    Args:
        task_id: Download task ID
        update: Progress update data
    """
    message = {
        "type": "progress",
        "task_id": task_id,
        "timestamp": datetime.utcnow().isoformat(),
        **update
    }
    await manager.broadcast(message)


async def broadcast_log_message(level: str, message: str):
    """
    Broadcast a log message to all connected clients.
    
    Args:
        level: Log level (INFO, WARNING, ERROR, etc.)
        message: Log message
    """
    log_message = {
        "type": "log",
        "level": level,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast(log_message)
