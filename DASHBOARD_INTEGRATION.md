# Dashboard Integration Guide

## Overview
The CommandCenterDashboard provides a modern tabbed interface to replace the traditional single-view UI.

## Integration Steps

### 1. Import the Dashboard in ui.py

Add to imports section:
```python
from app.window.dashboard import CommandCenterDashboard
from app.models.download_queue import DownloadQueue
from app.dialogs.queue_dialog import QueueDialog
```

### 2. Initialize Dashboard in __init__

After existing initialization, add:
```python
# Initialize download queue
self.download_queue = DownloadQueue(on_change=self.on_queue_changed)

# Create dashboard (replaces traditional UI)
self.dashboard = CommandCenterDashboard(
    self,
    tr=self.tr,
    on_download=self.start_download_from_dashboard,
    on_folder_select=self.select_folder
)
self.dashboard.pack(fill="both", expand=True)
```

### 3. Add Helper Methods

```python
def start_download_from_dashboard(self, url: str, folder: str):
    """Start download from dashboard."""
    # Add to queue
    self.download_queue.add(url, folder)
    self.add_log_message_safe(f"Added to queue: {url}")
    
    # Process queue if not already downloading
    self.process_queue()

def on_queue_changed(self):
    """Called when queue changes."""
    # Update dashboard stats
    stats = self.download_queue.get_stats()
    self.dashboard.update_stats(
        total=stats['total'],
        active=stats['downloading'],
        completed=stats['completed'],
        failed=stats['failed']
    )

def show_queue_manager(self):
    """Show the queue manager dialog."""
    queue_dialog = QueueDialog(self, self.download_queue, self.tr)
    queue_dialog.focus_set()

def process_queue(self):
    """Process next pending item in queue."""
    item = self.download_queue.get_next_pending()
    if item and not hasattr(self, '_is_downloading'):
        self._is_downloading = True
        self.download_queue.update_status(item.id, QueueItemStatus.DOWNLOADING)
        
        # Start actual download
        threading.Thread(
            target=self.download_from_queue_item,
            args=(item,),
            daemon=True
        ).start()

def download_from_queue_item(self, item):
    """Download a specific queue item."""
    try:
        # Use existing start_download logic but with queue item
        # Update progress via: self.download_queue.update_status(item.id, status, progress)
        pass
    finally:
        self._is_downloading = False
        self.process_queue()  # Process next item
```

### 4. Update Menu Bar Integration

In menu bar initialization, add Queue callback:
```python
from app.window.menu_bar import MenuBar

self.menu_bar = MenuBar(
    self,
    tr=self.tr,
    on_settings=self.settings_window.show_settings,
    on_about=self.about_window.show_about,
    on_donors=self.show_donors_modal,
    on_queue=self.show_queue_manager,  # NEW
    github_stars=self.github_stars,
    github_icon=self.github_icon,
    discord_icon=self.discord_icon,
    patreon_icon=self.patreon_icon
)
self.menu_bar.pack(fill="x", side="top")
```

### 5. Optional: Dual Mode Support

To support both classic and dashboard views:

```python
def __init__(self):
    # ... existing init ...
    
    # Check settings for UI mode
    ui_mode = self.settings.get('ui_mode', 'dashboard')  # or 'classic'
    
    if ui_mode == 'dashboard':
        self.init_dashboard_ui()
    else:
        self.init_classic_ui()

def init_dashboard_ui(self):
    """Initialize modern dashboard interface."""
    self.dashboard = CommandCenterDashboard(...)
    self.dashboard.pack(fill="both", expand=True)

def init_classic_ui(self):
    """Initialize traditional interface."""
    self.initialize_ui()  # Existing method
```

## Features Provided by Dashboard

### Home Tab
- Multi-line URL input for batch downloads
- Folder selection
- Quick stats cards (Total, Active, Completed, Failed)
- Large download button

### Queue Tab
- Placeholder for queue integration
- Will embed QueueDialog functionality

### Gallery Tab
- Search bar for media
- Filter buttons (All, Images, Videos, Other)
- Grid view of downloaded media
- Placeholder for media thumbnails

### History Tab
- Searchable download history
- Export functionality
- Statistics summary
- List of all past downloads with status

## Benefits

1. **Modern UX**: Tab-based navigation is intuitive
2. **Better Organization**: Separate concerns into dedicated views
3. **Batch Input**: Multi-line URL textbox
4. **Visual Feedback**: Color-coded status indicators
5. **Statistics**: Real-time stats on home tab
6. **History**: Persistent record of all downloads
7. **Gallery**: Built-in media browser

## Next Steps

1. Integrate dashboard into ui.py
2. Connect queue manager to queue tab
3. Implement gallery media loading
4. Implement history database queries
5. Add media preview/viewer
6. Add export functionality
