import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.api.services.queue_service import QueueService
from app.models.download_queue import QueueItemStatus
from backend.api.services.queue_service import get_queue

client = TestClient(app)

@pytest.fixture
def clean_queue():
    queue = QueueService.get_all_items()
    for item in queue:
        QueueService.remove_item(item.id)
    yield
    # Cleanup after test if needed
    queue = QueueService.get_all_items()
    for item in queue:
        QueueService.remove_item(item.id)

def test_add_to_queue(clean_queue):
    response = client.post(
        "/api/queue/add",
        json={
            "urls": ["https://example.com/video"],
            "options": {"download_videos": True},
            "priority": 2
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["url"] == "https://example.com/video"
    assert data[0]["status"] == "pending"

def test_get_queue(clean_queue):
    client.post(
        "/api/queue/add",
        json={"urls": ["https://example.com/1"], "priority": 2}
    )
    client.post(
        "/api/queue/add",
        json={"urls": ["https://example.com/2"], "priority": 2}
    )

    response = client.get("/api/queue/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_pause_resume(clean_queue):
    add_resp = client.post(
        "/api/queue/add",
        json={"urls": ["https://example.com/pause"], "priority": 2}
    )
    item_id = add_resp.json()[0]["id"]

    # Simulate downloading status (usually done by worker)
    queue = get_queue()
    queue.update_status(item_id, QueueItemStatus.DOWNLOADING)

    # Pause
    response = client.post(f"/api/queue/pause/{item_id}")
    assert response.status_code == 200

    item = queue.get(item_id)
    assert item.status == QueueItemStatus.PAUSED

    # Resume
    response = client.post(f"/api/queue/resume/{item_id}")
    assert response.status_code == 200

    item = queue.get(item_id)
    assert item.status == QueueItemStatus.PENDING

def test_advanced_options(clean_queue):
    response = client.post(
        "/api/queue/add",
        json={
            "urls": ["https://example.com/advanced"],
            "options": {
                "download_videos": True,
                "ytdlp_options": {
                    "format_selector": "bestaudio",
                    "download_subtitles": True
                }
            },
            "priority": 1
        }
    )
    assert response.status_code == 200
    data = response.json()
    # Check if options are preserved
    # Note: options in response might be converted back to schema structure or dict
    # QueueItemSchema options is Optional[DownloadOptionsSchema]
    # So it should be a dict in JSON response
    assert data[0]["options"]["ytdlp_options"]["format_selector"] == "bestaudio"
    assert data[0]["options"]["ytdlp_options"]["download_subtitles"] == True
