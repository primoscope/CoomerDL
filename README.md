![Windows Compatibility](https://img.shields.io/badge/Windows-10%2C%2011-blue)
![Downloads](https://img.shields.io/github/downloads/emy69/CoomerDL/total)

# CoomerDL - Universal Media Archiver

**CoomerDL** is a Python-based desktop application that has evolved into a **Universal Media Archiver**. It supports downloading images, videos, and galleries from **1000+ websites** through integrated engines (yt-dlp, gallery-dl) while maintaining specialized, high-speed scrapers for sites like Coomer, Kemono, and SimpCity.

---

## 📋 Quick Summary (for AI Agents)

**What**: Universal media archiver with three engines:
1. **Native Engine** (specialized): Coomer, Kemono, Bunkr, Erome, SimpCity, jpg5 (fast, purpose-built)
2. **Universal Video Engine** (yt-dlp): YouTube, Twitter/X, Reddit, TikTok, Instagram, Twitch, and 1000+ sites
3. **Universal Gallery Engine** (gallery-dl): DeviantArt, Pixiv, image boards, and galleries

**Tech Stack**: Python 3.8+, CustomTkinter (GUI), SQLite (download tracking + job history), yt-dlp, gallery-dl, requests (HTTP)

**Architecture**: 
- `app/` - UI components (CustomTkinter)
- `downloader/` - Multi-engine download system
  - `base.py` - BaseDownloader abstract class with standardized interface
  - `factory.py` - Smart URL routing with `can_handle()` classmethod pattern
  - `ytdlp_adapter.py` - yt-dlp integration (1000+ sites)
  - `gallery.py` - gallery-dl integration (image galleries)
  - `queue.py` - Unified job queue manager with event callbacks
  - `history.py` - SQLite persistence for jobs and events
  - `models.py` - JobStatus, ItemStatus, DownloadEvent dataclasses
  - `policies.py` - RetryPolicy, DomainPolicy for "press & forget" automation
  - `ratelimiter.py` - Per-domain concurrency and rate limiting
- `resources/config/` - Settings JSON, SQLite DB, cookies

**Key Features**:
- ✅ **Universal Mode**: Support for 1000+ sites via yt-dlp and gallery-dl
- ✅ **Smart Routing**: Factory pattern with 4-tier fallback (native → gallery → yt-dlp → generic)
- ✅ **Job Queue System**: Persistent job history, crash recovery, event-driven UI
- ✅ **Press & Forget**: Exponential backoff + jitter, per-domain rate limiting, auto-retry
- ✅ **Browser Cookie Import**: Automatic authentication from Chrome/Firefox/Edge
- ✅ **FFmpeg Integration**: Video/audio merging, format conversion, metadata embedding
- ✅ Thread-safe cancellation with `threading.Event()`
- ✅ Progress tracking with throttled callbacks (10 FPS)
- ✅ SQLite caching for duplicate detection (indexed queries)
- ✅ Connection pooling for faster downloads
- ✅ Multi-language support (i18n)

**Performance**:
- Startup: <1s (with indexed DB queries)
- Memory: ~25MB baseline (no cache preload)
- Concurrent downloads: 5-20 threads (configurable)
- Per-domain rate limiting: 2 concurrent requests, 1s minimum interval

**For Development**:
- See `ROADMAP.md` for tasks and priorities
- See `tests/CONTRACTS.md` for system behavior contracts
- See `AI_AGENT_WORKFLOW.md` for development workflows
- Run tests: `pytest tests/` (241 tests, all offline/deterministic)
- Use `python main.py` to run the application

---

## Support My Work

If you find this tool helpful, please consider supporting my efforts:

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-FFDD00.svg?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/emy_69)
[![Support on Patreon](https://img.shields.io/badge/Support%20on%20Patreon-FF424D.svg?style=for-the-badge&logo=patreon&logoColor=white)](https://www.patreon.com/emy69)


---

## Features

### 🌍 Universal Mode (NEW)
- **1000+ Supported Sites**: YouTube, Twitter/X, Reddit, TikTok, Instagram, Twitch, and more via yt-dlp
- **Gallery Support**: DeviantArt, Pixiv, image boards via gallery-dl
- **Smart Format Selection**: Best video+audio merge, audio-only, low quality modes
- **Browser Cookie Import**: Auto-authenticate from Chrome, Firefox, or Edge
- **Metadata Embedding**: Thumbnails, subtitles, and video metadata

### 🤖 Press & Forget Automation (NEW)
- **Auto-Retry**: Exponential backoff with jitter (1s → 2s → 4s → 8s, max 30s)
- **Rate Limiting**: Per-domain concurrency caps and minimum request intervals
- **Crash Recovery**: Jobs resume from where they stopped after app restart
- **Duplicate Prevention**: URL-based and hash-based duplicate detection

### 📦 Job Queue System (NEW)
- **Persistent History**: All jobs and events stored in SQLite database
- **Event-Driven UI**: Backend emits events (JOB_ADDED, JOB_PROGRESS, JOB_DONE, etc.)
- **Cancellation**: Clean stop within 2 seconds, partial file cleanup
- **Status Tracking**: PENDING → RUNNING → COMPLETED/FAILED/CANCELLED

### Download Images and Videos
- **Multithreaded Downloads**: Boosts download speed by utilizing multiple threads.
- **Progress Feedback**: Real-time progress updates during downloads.
- **Queue Management**: Efficiently handles large download queues.

**Supported File Extensions**:
- **Videos**: `.mp4`, `.mkv`, `.webm`, `.mov`, `.avi`, `.flv`, `.wmv`, `.m4v`
- **Images**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`
- **Documents**: `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`
- **Compressed**: `.zip`, `.rar`, `.7z`, `.tar`, `.gz`

---

## Supported Sites

### 🏠 Native Scrapers (Optimized)
- [coomer.su](https://coomer.su/)  
- [kemono.su](https://kemono.su/)  
- [erome.com](https://www.erome.com/)  
- [bunkr-albums.io](https://bunkr-albums.io/)  
- [simpcity.su](https://simpcity.su/)  
- [jpg5.su](https://jpg5.su/)  

### 🎬 Universal Video Engine (yt-dlp) - 1000+ Sites
- **Video Platforms**: YouTube, Vimeo, Dailymotion, Twitch, etc.
- **Social Media**: Twitter/X, Reddit, TikTok, Instagram, Facebook, etc.
- **Adult Sites**: (yt-dlp supported sites)
- **And many more**: [Full yt-dlp supported sites list](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

### 🖼️ Universal Gallery Engine (gallery-dl) - 100+ Sites
- **Art Platforms**: DeviantArt, Pixiv, ArtStation
- **Image Boards**: Various supported boards
- **Social**: Tumblr, Pinterest, etc.
- **And more**: [Full gallery-dl supported sites list](https://github.com/mikf/gallery-dl/blob/master/docs/supportedsites.md)  

---

## CLI Tools

If you prefer using command-line interfaces, check out the following projects:

- **[Coomer CLI](https://github.com/Emy69/Coomer-cli)**  
  A CLI tool for downloading media from Coomer and similar sites. It offers customizable options for file naming, download modes, rate limiting, checksum verification, and more.

- **[Simpcity CLI](https://github.com/Emy69/SimpCityCLI)**  
  A CLI tool specifically designed for downloading media from Simpcity. It shares many features with Coomer CLI and is tailored for the Simpcity platform.

---


## Language Support

- [Español](#)  
- [English](#)  
- [日本語 (Japanese)](#)  
- [中文 (Chinese)](#)  
- [Français (French)](#)  
- [Русский (Russian)](#)  

---

## Community

Have questions or just want to say hi? Join the Discord server:

[![Join Discord](https://img.shields.io/badge/Join-Discord-7289DA.svg?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/ku8gSPsesh)

---

## Downloads

- **Latest Version**: Visit the [Releases Page](https://github.com/Emy69/CoomerDL/releases) to download the newest version.

---

## Quick Start

### Installation

1. **Install Python 3.8+** (if not already installed)
2. **Clone the repository**:
   ```sh
   git clone https://github.com/Emy69/CoomerDL.git
   cd CoomerDL
   ```
3. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```
4. **Run the application**:
   ```sh
   python main.py
   ```

> **Note**: On Linux, you may need to install tkinter separately: `sudo apt install python3-tk`
> 
> For detailed installation instructions and troubleshooting, see [Installation & Troubleshooting](#installation--troubleshooting) below.

---

## Usage

1. Launch the application.
2. Paste the URL of the image or video you want to download.
3. Click **Download** and wait for the process to finish.

![Usage GIF](https://github.com/Emy69/CoomerDL/blob/main/resources/screenshots/0627.gif)

---

## Installation & Troubleshooting

### System Requirements

- **Python**: 3.8 or higher (3.9, 3.10, 3.11, 3.12 supported)
- **Operating Systems**: Windows 10/11, macOS, Linux
- **Memory**: Minimum 2GB RAM recommended
- **Storage**: ~500MB for application and dependencies

### Step-by-Step Installation Guide

#### 1. Install Python
Make sure Python 3.8+ is installed:
```sh
python --version  # Should show Python 3.8.x or higher
```

If not installed:
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **macOS**: `brew install python@3.11` or download from python.org
- **Linux**: Usually pre-installed, or `sudo apt install python3 python3-pip`

#### 2. Install System Dependencies (Linux only)
On Linux, tkinter needs to be installed separately:
```sh
# Ubuntu/Debian
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```

#### 3. Clone the Repository
```sh
git clone https://github.com/Emy69/CoomerDL.git
cd CoomerDL
```

#### 4. Install Python Dependencies
```sh
pip install -r requirements.txt
```

Or if you prefer using pip3:
```sh
pip3 install -r requirements.txt
```

#### 5. (Optional) Install FFmpeg
For Universal Mode (yt-dlp) video/audio merging:
- **Windows**: `winget install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/download.html)
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

#### 6. Run the Application
```sh
python main.py
```

### Common Issues and Solutions

#### Issue: `ModuleNotFoundError: No module named 'tkinter'`

**Solution (Linux)**:
```sh
sudo apt install python3-tk  # Ubuntu/Debian
sudo dnf install python3-tkinter  # Fedora
sudo pacman -S tk  # Arch Linux
```

**Solution (Windows/macOS)**:
Tkinter should come with Python. Reinstall Python from [python.org](https://www.python.org/downloads/) and make sure to check "Install tkinter" during installation.

#### Issue: `TypeError: DownloadQueue.__init__() got an unexpected keyword argument`

**Solution**:
Make sure you're using the latest version of the code:
```sh
git pull origin main  # or master
pip install -r requirements.txt --upgrade
```

#### Issue: `ModuleNotFoundError: No module named 'customtkinter'` (or other packages)

**Solution**:
Install/reinstall dependencies:
```sh
pip install -r requirements.txt --force-reinstall
```

#### Issue: FFmpeg not found

**Solution**:
1. Install FFmpeg (see step 5 above)
2. Make sure FFmpeg is in your system PATH
3. Verify installation: `ffmpeg -version`

The app will work without FFmpeg, but video/audio merging in Universal Mode won't be available.

#### Issue: `ImportError: cannot import name 'ImageDownloaderApp'`

**Solution**:
This usually means there's a syntax error or missing dependency. Check:
```sh
python -c "import app.ui"  # Test if module loads
pip list  # Check installed packages
```

#### Issue: Downloads fail with 403/429 errors

**Solution**:
- **403 Forbidden**: Site may require cookies. Use browser cookie import feature in settings.
- **429 Too Many Requests**: Rate limiting. Wait a few minutes and try again with lower concurrency.

#### Issue: Application starts but UI doesn't show

**Solution (Windows)**:
```sh
# Try running with pythonw instead of python
pythonw main.py
```

**Solution (Linux/macOS)**:
Check if you have a display server running. For headless servers, CoomerDL requires a GUI environment.

#### Issue: High memory usage

**Solution**:
- Reduce concurrent downloads in settings
- Clear completed downloads from queue
- Restart the application periodically for long sessions

#### Issue: Database locked errors

**Solution**:
Close other instances of CoomerDL. Only one instance should run at a time.

### Getting Help

If you encounter issues not listed here:

1. **Check existing issues**: [GitHub Issues](https://github.com/Emy69/CoomerDL/issues)
2. **Join Discord**: [Discord Server](https://discord.gg/ku8gSPsesh)
3. **Create a new issue**: Include:
   - Python version (`python --version`)
   - OS and version
   - Error message (full traceback)
   - Steps to reproduce

---

## Contributing with AI Coding Agents

This repository is optimized for AI coding agents (GitHub Copilot, Claude, GPT-4, etc.). The documentation is structured to help agents understand and implement changes effectively.

### Documentation Structure

| File | Purpose | Use When |
|------|---------|----------|
| [ROADMAP.md](ROADMAP.md) | User-friendly feature roadmap and planned features | Understanding what's available and coming soon |
| [ROADMAP_TASKS_BY_PRIORITY.md](ROADMAP_TASKS_BY_PRIORITY.md) | Quick summary of all open tasks organized by priority | Getting a fast overview of what needs to be done |
| [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) | Technical roadmap with detailed task breakdowns | Finding what to work on (developers) |
| [TASKS.md](TASKS.md) | Detailed task breakdowns with acceptance criteria | Implementing a specific task |
| [SPECIFICATIONS.md](SPECIFICATIONS.md) | Full code specifications for new features | Building new classes/functions |
| [POTENTIAL_ISSUES.md](POTENTIAL_ISSUES.md) | Known blockers and edge cases | Understanding risks |
| [AGENT_VALIDATION_REPORT.md](AGENT_VALIDATION_REPORT.md) | AI agent configuration validation results | Verifying agent setup and installation |

### How to Prompt AI Agents

#### For Bug Fixes
```
Read ROADMAP.md and implement task BUG-001.

Context: This is a Python desktop app using CustomTkinter.
The bug is in downloader/downloader.py.
Follow the FIND/REPLACE instructions in the task.
```

#### For New Features
```
Read ROADMAP.md and SPECIFICATIONS.md, then implement FEATURE-002 (BaseDownloader class).

Requirements:
1. Create the new file at downloader/base.py
2. Follow the class specification in SPECIFICATIONS.md
3. Include all abstract methods and data classes
4. Ensure backward compatibility
```

#### For Refactoring
```
Read ROADMAP.md and implement REFACTOR-001 (standardize cancel mechanisms).

Files to modify: downloader/bunkr.py, downloader/erome.py, downloader/simpcity.py
Follow the step-by-step instructions in the task.
Test by running: python main.py
```

### Best Practices for Agent Prompts

1. **Always reference the task ID** (e.g., BUG-001, FEATURE-002)
2. **Point to the documentation files** - agents work better with context
3. **Specify the scope** - "only modify X file" prevents over-engineering
4. **Include test instructions** - so the agent can verify the fix
5. **Mention constraints** - "maintain backward compatibility", "minimal changes"

### Example Workflow

```bash
# 1. Ask agent to read the roadmap and pick a task
"Read ROADMAP.md and list all 🔴 CRITICAL tasks"

# 2. Ask agent to implement one task
"Implement BUG-001 from ROADMAP.md. Show me the exact changes."

# 3. Verify the changes
python main.py

# 4. Ask agent to run tests if applicable
"Run any tests related to the downloader module"
```

### Task Priority Guide

| Icon | Priority | Agent Instruction |
|------|----------|-------------------|
| 🔴 | CRITICAL | "Fix this bug first, it causes crashes" |
| 🟠 | HIGH | "Important feature, implement carefully" |
| 🟡 | MEDIUM | "Improvement, make minimal changes" |
| 🟢 | LOW | "Nice-to-have, only if time permits" |

### Quick Agent Commands

Copy-paste these prompts to get started:

**List all tasks:**
```
Read ROADMAP.md and give me a summary of all open tasks by priority.
```

**Fix a specific bug:**
```
Read ROADMAP.md task BUG-001. Show the current code, explain the bug, and provide the fix.
```

**Implement a feature:**
```
Read SPECIFICATIONS.md section "BaseDownloader" and create the file downloader/base.py with the full implementation.
```

**Check for issues:**
```
Read POTENTIAL_ISSUES.md and tell me which issues might affect task FEATURE-001.
```

### Validation and Testing

The repository includes validation scripts to ensure AI agent configurations and installations are working correctly:

**Validate agent configurations:**
```bash
python validate_agents.py
```
This checks that all `.agent.md` files in `.github/agents/` are properly formatted with required fields.

**Test installation:**
```bash
python test_installation.py
```
This verifies that all dependencies and application modules can be imported successfully.

**Run full test suite:**
```bash
pytest tests/ -v
```
Runs all 241 tests to validate codebase functionality.

For detailed validation results, see [AGENT_VALIDATION_REPORT.md](AGENT_VALIDATION_REPORT.md).
