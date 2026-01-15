# Missing Features & Technical Debt

**Date**: January 15, 2026
**Status**: Analysis Complete

This document outlines features that were claimed to be complete but are missing or incomplete, and technical debt identified during the code audit.

## 1. Queue System

### Status: ⚠️ Incomplete
- **Claim**: "Phase 1-4: ✅ COMPLETE BaseDownloader, Queue, Tests"
- **Reality**:
    - `DownloadQueue` (data structure) exists and persists to JSON.
    - `QueuePage` (UI) exists but the "Process Queue" button explicitly says "Feature unavailable".
    - No background worker exists to process the queue.

### Action Plan
- [x] Create `QueueProcessor` skeleton (`app/controllers/queue_processor.py`).
- [ ] Integrate `QueueProcessor` into `SidebarApp`.
- [ ] Implement legacy downloader support in `QueueProcessor` (for Coomer/Kemono).
- [ ] Enable "Process Queue" button in UI.

## 2. Architecture Hybrid State

### Status: ⚠️ Mixed
- **Claim**: "Base Downloader Architecture: Robust, extensible base class for all downloaders."
- **Reality**:
    - `BaseDownloader` and `DownloaderFactory` exist.
    - `YtDlpDownloader` uses the new architecture.
    - `Jpg5Downloader` was legacy (Refactored to new architecture on Jan 15, 2026).
    - `Downloader` (monolithic class in `downloader/downloader.py`) handles Coomer/Kemono/SimpCity/Erome/Bunkr and does NOT use the new architecture.

### Action Plan
- [ ] Refactor `Downloader` class:
    - Extract `CoomerDownloader` -> `downloader/coomer.py`
    - Extract `KemonoDownloader` -> `downloader/kemono.py`
    - Extract `SimpCityDownloader` -> `downloader/simpcity.py` (if not already done)
    - Extract `EromeDownloader` -> `downloader/erome.py` (if not already done)
    - Extract `BunkrDownloader` -> `downloader/bunkr.py` (if not already done)
- [ ] Register all new downloaders with `DownloaderFactory`.
- [ ] Deprecate and remove the monolithic `Downloader` class.

## 3. Test Coverage

### Status: ❓ Unknown/Low
- `tests/` directory exists but coverage is likely low for the legacy `Downloader` class.
- New architecture (`BaseDownloader`) needs comprehensive tests.

### Action Plan
- [ ] Add unit tests for `QueueProcessor`.
- [ ] Add unit tests for `Jpg5Downloader` (newly refactored).
- [ ] Add integration tests for `DownloaderFactory`.

## 4. Build & Dependencies

### Status: ✅ Improved
- Dependencies were unpinned.
- **Action**: Pinned dependencies in `requirements.txt` and updated `environment.yml`.
- **Action**: Verified build scripts.

