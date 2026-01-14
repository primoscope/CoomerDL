# CoomerDL API Documentation

Complete REST API documentation for the CoomerDL web application backend.

## Base URL

- **Local Development**: `http://localhost:8080/api`
- **Production**: `https://your-service.run.app/api`

## Authentication

Currently, the API is open. For production deployments, implement JWT authentication:

```http
Authorization: Bearer <token>
```

---

## Endpoints

### Health Check

Check if the API is running.

```http
GET /health
```

**Response**
```json
{
  "status": "healthy",
  "service": "CoomerDL",
  "version": "2.0.0"
}
```

---

## Downloads

### Start Download

Start one or more downloads.

```http
POST /api/downloads/start
```

**Request Body**
```json
{
  "urls": [
    "https://example.com/media",
    "https://example.com/gallery"
  ],
  "download_folder": "/downloads/optional",
  "options": {
    "download_images": true,
    "download_videos": true,
    "download_compressed": true,
    "download_documents": true,
    "max_retries": 3,
    "retry_interval": 2.0,
    "proxy_type": "none",
    "proxy_url": "",
    "bandwidth_limit_kbps": 0
  }
}
```

**Response**
```json
[
  {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "started",
    "message": "Download started for https://example.com/media"
  }
]
```

**Status Codes**
- `200 OK` - Downloads started successfully
- `400 Bad Request` - Invalid request body
- `500 Internal Server Error` - Server error

---

### Get Download Status

Get the current status of a download.

```http
GET /api/downloads/status/{task_id}
```

**Path Parameters**
- `task_id` (string, required) - The task ID returned from start download

**Response**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "downloading",
  "url": "https://example.com/media",
  "progress": 45.5,
  "current_file": "image_001.jpg",
  "total_files": 100,
  "completed_files": 45,
  "failed_files": 0,
  "download_speed": 1048576,
  "eta_seconds": 120,
  "error_message": null,
  "created_at": "2024-01-14T10:00:00Z",
  "updated_at": "2024-01-14T10:05:00Z"
}
```

**Status Values**
- `pending` - Download queued but not started
- `downloading` - Download in progress
- `paused` - Download paused
- `completed` - Download finished successfully
- `failed` - Download failed
- `cancelled` - Download cancelled by user
- `skipped` - Download skipped (duplicate)

**Status Codes**
- `200 OK` - Status retrieved successfully
- `404 Not Found` - Task ID not found

---

### Cancel Download

Cancel an active download.

```http
POST /api/downloads/cancel/{task_id}
```

**Path Parameters**
- `task_id` (string, required) - The task ID to cancel

**Response**
```json
{
  "message": "Download 550e8400-e29b-41d4-a716-446655440000 cancelled"
}
```

**Status Codes**
- `200 OK` - Download cancelled successfully
- `404 Not Found` - Task ID not found

---

### Get Active Downloads

Get all currently active downloads.

```http
GET /api/downloads/active
```

**Response**
```json
{
  "count": 2,
  "downloads": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "downloading",
      "url": "https://example.com/media",
      "progress": 45.5,
      "current_file": "image_001.jpg",
      "total_files": 100,
      "completed_files": 45,
      "failed_files": 0,
      "download_speed": 1048576,
      "eta_seconds": 120
    }
  ]
}
```

---

## WebSocket Endpoints

### Progress Updates

Real-time progress updates for downloads.

```
ws://localhost:8080/ws/progress
```

**Client → Server**
```json
"ping"
```

**Server → Client**
```json
{
  "type": "progress",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "downloading",
  "progress": 45.5,
  "current_file": "image_001.jpg",
  "download_speed": 1048576,
  "eta_seconds": 120,
  "timestamp": "2024-01-14T10:05:00Z"
}
```

---

### Log Streaming

Real-time log messages.

```
ws://localhost:8080/ws/logs
```

**Client → Server**
```json
"ping"
```

**Server → Client**
```json
{
  "type": "log",
  "level": "INFO",
  "message": "Starting download for https://example.com/media",
  "timestamp": "2024-01-14T10:05:00Z"
}
```

**Log Levels**
- `INFO` - Informational messages
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `SUCCESS` - Success messages

---

## Data Models

### DownloadOptions

```typescript
{
  download_images: boolean        // Download image files
  download_videos: boolean        // Download video files
  download_compressed: boolean    // Download compressed files
  download_documents: boolean     // Download document files
  max_retries: number            // Maximum retry attempts (default: 3)
  retry_interval: number         // Seconds between retries (default: 2.0)
  chunk_size: number             // Download chunk size in bytes
  timeout: number                // Request timeout in seconds
  min_file_size: number          // Minimum file size in bytes (0 = no limit)
  max_file_size: number          // Maximum file size in bytes (0 = no limit)
  date_from?: string             // Start date filter (ISO format)
  date_to?: string               // End date filter (ISO format)
  excluded_extensions: string[]  // File extensions to skip
  proxy_type: string             // Proxy type: "none", "system", "custom"
  proxy_url: string              // Proxy URL for custom proxy
  user_agent?: string            // Custom user agent
  bandwidth_limit_kbps: number   // Bandwidth limit in KB/s (0 = unlimited)
  connection_timeout: number     // Connection timeout in seconds
  read_timeout: number           // Read timeout in seconds
}
```

---

## Error Handling

All endpoints return errors in this format:

```json
{
  "detail": "Error message here"
}
```

**Common Error Codes**
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

---

## Rate Limiting

To prevent abuse, the API implements rate limiting:

- **Per IP**: 100 requests per minute
- **Per Task**: 10 concurrent downloads per user

**Rate Limit Headers**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1610000000
```

---

## Examples

### cURL Examples

**Start a download**
```bash
curl -X POST http://localhost:8080/api/downloads/start \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://example.com/media"],
    "options": {
      "download_images": true,
      "download_videos": true
    }
  }'
```

**Get download status**
```bash
curl http://localhost:8080/api/downloads/status/550e8400-e29b-41d4-a716-446655440000
```

**Cancel download**
```bash
curl -X POST http://localhost:8080/api/downloads/cancel/550e8400-e29b-41d4-a716-446655440000
```

### JavaScript Examples

**Using Fetch API**
```javascript
// Start download
const response = await fetch('/api/downloads/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    urls: ['https://example.com/media'],
    options: {
      download_images: true,
      download_videos: true
    }
  })
});

const data = await response.json();
console.log('Task ID:', data[0].task_id);
```

**WebSocket Connection**
```javascript
const ws = new WebSocket('ws://localhost:8080/ws/progress');

ws.onopen = () => {
  console.log('Connected to progress updates');
};

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Progress:', update.progress);
};

// Send heartbeat
setInterval(() => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send('ping');
  }
}, 30000);
```

### Python Examples

**Using requests library**
```python
import requests

# Start download
response = requests.post('http://localhost:8080/api/downloads/start', json={
    'urls': ['https://example.com/media'],
    'options': {
        'download_images': True,
        'download_videos': True
    }
})

task_id = response.json()[0]['task_id']
print(f'Task ID: {task_id}')

# Check status
status = requests.get(f'http://localhost:8080/api/downloads/status/{task_id}')
print(f'Progress: {status.json()["progress"]}%')
```

---

## Interactive Documentation

The API also provides interactive documentation:

- **Swagger UI**: `http://localhost:8080/api/docs`
- **ReDoc**: `http://localhost:8080/api/redoc`

These interfaces allow you to:
- Browse all endpoints
- See request/response schemas
- Try out API calls directly
- Generate code examples

---

## Webhook Support (Future)

Coming soon: Webhook notifications for download events.

```json
{
  "event": "download.completed",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://example.com/media",
  "total_files": 100,
  "timestamp": "2024-01-14T10:10:00Z"
}
```

---

## Support

- **Issues**: https://github.com/primoscope/CoomerDL/issues
- **Documentation**: https://github.com/primoscope/CoomerDL
- **API Status**: Check `/health` endpoint
