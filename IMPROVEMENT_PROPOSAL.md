# 🚀 CoomerDL Improvement Proposal

## 🎨 UI/UX Overhaul: The "Command Center" Redesign

The current interface is functional but relies on a vertical stack of panels. To modernize the application and handle the increasing number of features (Queue, Settings, History, Dashboard), we propose a **Sidebar Navigation Architecture**.

### 1. Structural Redesign (Sidebar Layout)
Transition from a single-page scrolling view to a distinct **"View-Controller"** model.

*   **Left Sidebar (Fixed):**
    *   **App Logo & Version**
    *   **Navigation Tabs:**
        *   📥 **Downloader** (The main input/action area)
        *   📋 **Queue** (Active/Pending downloads)
        *   📊 **History** (Searchable database of past downloads)
        *   ⚙️ **Settings** (Config, Accounts, Paths)
        *   ℹ️ **About/Support**
    *   **Bottom of Sidebar:**
        *   **Quick Toggle:** Clipboard Monitor (On/Off)
        *   **Connection Status:** (Online/Offline indicator)

*   **Right Content Area (Dynamic):**
    *   Swaps out the content frame based on the selected Sidebar tab.
    *   **Downloader View:** Kept clean. Input bar at top, Options in a collapsible "Advanced" section, and a large "Status/Log" area.

### 2. Visual Polish
*   **Icons:** Replace text buttons with high-quality SVG icons (using `CTkImage` with vector assets).
*   **Animations:** Smooth transitions when switching views or expanding the "Advanced Options" panel.
*   **Theming:** Add an "Accent Color" picker in settings to allow users to customize the `dark-blue` default to their preference (e.g., Purple, Green, Red).

---

## 🛠️ New Feature Recommendations

### 1. 🔍 Batch Link Analyzer (Pre-flight Check)
**Problem:** Users often paste a link without knowing if it contains 5 images or 5,000.
**Solution:**
*   **"Analyze" Button:** Next to "Download".
*   **Function:** Fetches the page metadata *without* downloading media.
*   **Preview Dialog:**
    *   "Found: 125 Images, 3 Videos"
    *   "Total Est. Size: ~450 MB"
    *   "Creator: [Name]"
    *   **Action:** "Download All", "Select Types", or "Cancel".

### 2. 📋 Clipboard Monitor & Auto-Paste
**Function:**
*   A background thread watches the system clipboard.
*   **Regex Matching:** If a URL matches a supported pattern (e.g., `coomer.su/user/...`, `youtube.com/watch...`), the app reacts.
*   **Modes:**
    *   *Auto-Paste:* Instantly puts the link in the input box.
    *   *Auto-Queue:* (Power User) Instantly adds it to the Download Queue without asking.

### 3. 🔭 "Watch Mode" (Subscriptions)
**Concept:** Turn the downloader into an archiver.
*   **Subscription List:** Users can "Subscribe" to a specific creator/profile URL.
*   **Background Worker:** Every X hours, the app checks these URLs for *new* posts since the last check.
*   **Auto-Download:** Automatically downloads new content to the creator's folder.

### 4. 📂 Smart Collections & Virtual Folders
**Concept:** improved file management.
*   **Tagging:** If the source site has tags (e.g., "Cosplay", "Outdoor"), save them to a local DB.
*   **Virtual Views:** Browse downloads not just by folder, but by Tag, Date Downloaded, or Media Type (e.g., "Show me all Videos from all creators").

---

## ⚡ Performance & Engineering

### 1. Integration of `aria2c`
*   **Why:** Python's HTTP libraries are good, but `aria2c` is the gold standard for high-speed, multi-connection downloads.
*   **Implementation:** `yt-dlp` already supports `aria2c` as an external downloader. We can expose this option in the UI for users who have it installed.

### 2. Database Optimization
*   As History grows (10k+ items), `SQLite` queries might slow down the UI if run on the main thread.
*   **Recommendation:** Ensure all DB operations are strictly async or threaded. Add indices on `url` and `date` columns.

### 3. Modular "Engine" System
*   Formalize the `DownloaderFactory` pattern (already in progress).
*   Make adding a new site scraper as easy as dropping a `.py` file into a `plugins/` folder (Plugin Architecture).

---

## 🧪 "Unique" Features (The "Wow" Factor)

### 1. 🖼️ "Gallery View" (Internal Viewer)
Instead of opening Windows Explorer, provide a simple grid view of the downloaded images *inside* the History tab. This makes the app feel like a complete media manager.

### 2. 🕵️ "Privacy Mode"
A "Panic Button" or hotkey that instantly minimizes the app to the tray and pauses all downloads/logs, useful for privacy.

### 3. 📦 "Archive Packer"
An option to automatically ZIP/7Z the folder after a download completes. Great for backing up to external drives.

---

## 📝 Immediate Implementation Plan (This Session)

1.  **UI Structure:** Implement the **Sidebar Navigation** system.
2.  **Core Feature:** Implement the **Batch Link Analyzer** (Count images/videos before download).
3.  **Utility:** Implement the **Clipboard Monitor**.
