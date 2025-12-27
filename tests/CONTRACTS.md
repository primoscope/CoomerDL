# CoomerDL Download System Contracts

> **Purpose**: Developer-facing documentation defining expected semantics and invariants for the download system. All tests should verify these contracts.

---

## Job Status Transitions

### Valid State Machine

```
                    ┌─────────────────┐
                    │                 │
                    ▼                 │
PENDING ──────► RUNNING ──────► COMPLETED
    │              │                 
    │              ├──────────► FAILED
    │              │                 
    │              └──────────► CANCELLED
    │                               ▲
    └───────────────────────────────┘
           (direct cancel)
```

### Transition Rules

| From | To | Trigger | Requirements |
|------|-----|---------|--------------|
| PENDING | RUNNING | `job.mark_started()` | Must set `started_at` |
| PENDING | CANCELLED | `queue.cancel_job()` | Must not have started downloading |
| RUNNING | COMPLETED | `job.mark_completed()` | All items processed, `completed_items + failed_items + skipped_items == total_items` |
| RUNNING | FAILED | `job.mark_failed(error)` | Unrecoverable error occurred |
| RUNNING | CANCELLED | User cancellation | Must stop downloads quickly (< 2 seconds) |

### Invalid Transitions

- COMPLETED → any other state
- FAILED → any other state  
- CANCELLED → any other state
- PAUSED → (reserved for future, currently unused)

---

## Item Status Transitions

### Valid State Machine

```
PENDING ──────► DOWNLOADING ──────► COMPLETED
    │              │                    │
    │              ├──────────► FAILED  │
    │              │                    │
    │              └──────────► CANCELLED
    │                               ▲
    └───────────────────────────────┘
           (direct skip)
    │
    └──────────────────────► SKIPPED
         (pre-download filter)
```

### Transition Rules

| From | To | Trigger | Requirements |
|------|-----|---------|--------------|
| PENDING | DOWNLOADING | Download starts | File download initiated |
| PENDING | SKIPPED | `should_skip_file()` returns True | Extension/size/date filter |
| DOWNLOADING | COMPLETED | Download finishes | File exists, size matches |
| DOWNLOADING | FAILED | Download error | Network error, 404, etc. |
| DOWNLOADING | CANCELLED | User cancellation | Partial file cleanup |

---

## Counter Semantics

### Definition of Counters

| Counter | Increments When | Notes |
|---------|-----------------|-------|
| `total_items` | Items discovered | Fixed once enumeration complete |
| `completed_items` | Item COMPLETED or SKIPPED | Includes successful skips |
| `failed_items` | Item FAILED | Excludes user cancellation |
| `skipped_items` | Item SKIPPED | Pre-download filter (extension/size/date) |

### Invariants

```python
# Always true for completed jobs
completed_items + failed_items + skipped_items == total_items

# Progress percentage
progress = completed_items / total_items * 100  # when total_items > 0

# Success determination
success = (failed_items == 0) and (status != CANCELLED)
```

### Counter Increment Order

1. **SKIPPED items**: `skipped_items += 1`, then `completed_items += 1`
2. **COMPLETED items**: `completed_items += 1` only
3. **FAILED items**: `failed_items += 1` only (not in completed_items)

---

## Cancellation Contract

### Requirements

1. **Response Time**: Download must stop within 2 seconds of cancellation request
2. **Cleanup**: Partial `.part` files must be deleted
3. **State**: Job status must be CANCELLED
4. **Items**: All in-progress items become CANCELLED

### Implementation Checklist

```python
# In download loop
if self.is_cancelled():
    # 1. Stop current operation
    # 2. Clean up partial files
    # 3. Return early with success=False
    return DownloadResult(success=False, ...)
```

### Threading Safety

- `cancel_event` must be `threading.Event()` (not boolean flag)
- Check `is_cancelled()` frequently in download loops
- Use `cancel_event.wait(timeout)` for interruptible sleeps

---

## Progress Reporting Contract

### `report_progress()` Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `downloaded` | int | Yes | Bytes downloaded for current file |
| `total` | int | Yes | Total bytes for current file (0 if unknown) |
| `file_id` | str | Recommended | Stable unique identifier for the file |
| `file_path` | str | Recommended | Destination path |
| `url` | str | Recommended | Source URL |
| `speed` | float | Optional | Download speed in bytes/sec |
| `eta` | int | Optional | Estimated time remaining in seconds |
| `status` | str | Optional | Status message (e.g., "Downloading", "Merging") |

### `report_global_progress()` Behavior

Called when:
- An item completes (COMPLETED)
- An item is skipped (SKIPPED)
- An item fails (FAILED)

Must increment `completed_items` counter before calling.

---

## DownloadResult Contract

### Required Fields

```python
@dataclass
class DownloadResult:
    success: bool              # True if job completed without fatal error
    total_files: int           # Total items discovered
    completed_files: int       # Items completed + skipped
    failed_files: List[str]    # List of failed file URLs/paths
    skipped_files: List[str]   # List of skipped file URLs/paths
    error_message: Optional[str] = None  # Only set if success=False
```

### Invariants

```python
# Always true
len(failed_files) == (total_files - completed_files) if not cancelled

# Success criteria
success == (len(failed_files) == 0 and not cancelled)

# Skipped files are still "completed"
completed_files >= len(skipped_files)
```

### Engine-Specific Notes

- **yt-dlp**: May report total_files=1 for single videos, even if multiple formats merged
- **gallery-dl**: total_files known after enumeration, before download starts
- **Native**: total_files discovered incrementally, may update during download

---

## Event Emission Order

### Standard Job Lifecycle Events

```
1. JOB_ADDED        - Job created and queued
2. JOB_STARTED      - Job execution begins
3. ITEM_PROGRESS*   - Repeated during download
4. ITEM_DONE*       - After each item completes
5. JOB_PROGRESS*    - After items complete
6. JOB_DONE         - Job execution ends
```

### Error Path Events

```
1. JOB_ADDED
2. JOB_STARTED
3. ...
4. JOB_ERROR        - Unrecoverable error (still emits JOB_DONE)
5. JOB_DONE
```

### Cancellation Path Events

```
1. JOB_ADDED
2. JOB_STARTED (maybe)
3. ...
4. JOB_CANCELLED    - User cancelled
5. JOB_DONE
```

### Event Payload Requirements

| Event | Required Payload |
|-------|------------------|
| JOB_ADDED | url, engine, output_folder |
| JOB_STARTED | url, engine |
| ITEM_PROGRESS | downloaded_bytes, total_bytes |
| ITEM_DONE | file_id, file_path, success |
| JOB_PROGRESS | completed_items, total_items |
| JOB_DONE | status, total_items, completed_items, failed_items, skipped_items |
| JOB_ERROR | error_message |
| JOB_CANCELLED | (none) |
| LOG | message, level |

---

## Retry Policy Contract

### Default Policy

```python
DEFAULT_RETRY_POLICY = RetryPolicy(
    max_attempts=5,
    base_delay=1.0,
    max_delay=30.0,
    jitter=0.2,
    retryable_statuses={429, 500, 502, 503, 504},
    retryable_exceptions=(requests.Timeout, requests.ConnectionError)
)
```

### Backoff Formula

```python
delay = min(base_delay * (2 ** attempt), max_delay)
delay *= (1 + random.uniform(-jitter, jitter))
```

### Retry Behavior

1. First attempt: immediate
2. Retry 1: ~1 second delay
3. Retry 2: ~2 seconds delay
4. Retry 3: ~4 seconds delay
5. Retry 4: ~8 seconds delay
6. Max delay capped at 30 seconds

---

## Rate Limiting Contract

### Domain Limiter Behavior

```python
# Per-domain concurrency: max 2 concurrent requests
# Per-domain delay: min 1 second between requests

with domain_limiter.limit("example.com"):
    response = requests.get(url)
```

### Thread Safety

- Semaphore-based concurrency limiting
- Lock-protected last-request tracking
- Safe for use from ThreadPoolExecutor workers

---

## File Naming Contract

### Sanitization Rules

```python
# Characters replaced with underscore
INVALID_CHARS = r'[<>:"/\\|?*\x00-\x1f]'

# Maximum filename length (excluding extension)
MAX_FILENAME_LENGTH = 200

# Truncation preserves extension
"very_long_name.mp4" -> "very_long_na....mp4"
```

### Output Template (yt-dlp)

```python
DEFAULT_OUTPUT_TEMPLATE = "%(uploader|Unknown)s/%(upload_date>%Y-%m-%d|)s%(title).200B [%(id)s].%(ext)s"
```

---

## History/Persistence Contract

### Database Schema

```sql
-- Jobs table
CREATE TABLE jobs (
    job_id TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    engine TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    started_at TEXT,
    finished_at TEXT,
    total_items INTEGER DEFAULT 0,
    completed_items INTEGER DEFAULT 0,
    failed_items INTEGER DEFAULT 0,
    skipped_items INTEGER DEFAULT 0,
    output_folder TEXT,
    error_message TEXT,
    options_json TEXT
);

-- Events table
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    type TEXT NOT NULL,
    payload_json TEXT,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
);

-- Job items table (for crash recovery)
CREATE TABLE job_items (
    job_id TEXT NOT NULL,
    item_key TEXT NOT NULL,
    status TEXT NOT NULL,
    file_path TEXT,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (job_id, item_key),
    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
);
```

### Crash Recovery Contract

1. On startup, load jobs with status RUNNING or PENDING
2. For RUNNING jobs (crashed mid-execution), reset to PENDING with JOB_ERROR event
3. Skip items already marked COMPLETED in job_items table
4. Resume from where crash occurred

---

## Test Categories

### Unit Tests (No Network)

- Model serialization/deserialization
- Counter arithmetic
- State transitions
- Backoff calculation
- URL canonicalization
- File name sanitization

### Integration Tests (Mocked Network)

- Full job lifecycle with mock HTTP
- Event emission order
- Cancellation during download
- Retry behavior
- Rate limiting

### System Tests (Optional, Behind Flag)

- Real downloads from supported sites
- End-to-end queue processing
- History persistence across restarts

---

## Verification Checklist

When implementing or modifying downloaders, verify:

- [ ] `total_items` is set before any downloads start
- [ ] `completed_items` increments on completion AND skip
- [ ] `failed_items` increments on failure only
- [ ] `skipped_items` increments on skip only
- [ ] Cancellation stops within 2 seconds
- [ ] Partial files are cleaned up
- [ ] `report_global_progress()` called after each item
- [ ] `report_progress()` includes file_id when possible
- [ ] DownloadResult matches final counters
- [ ] Events emitted in correct order

---

*Last updated: December 2024*
