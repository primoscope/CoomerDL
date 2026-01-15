# 🗺️ CoomerDL Roadmap

Welcome to the CoomerDL Roadmap! This document outlines our current features, what we're working on, and exciting ideas for the future. We'd love to hear your feedback and feature requests!

---

## 📋 Table of Contents

- [✨ What's New](#-whats-new)
- [🎯 Current Features](#-current-features)
- [🚧 In Development](#-in-development)
- [📅 Planned Features](#-planned-features)
- [💡 Future Ideas](#-future-ideas)
- [🗳️ Feature Requests](#️-feature-requests)

---

## ✨ What's New

### Version 2.0 - Universal Archiver Update

CoomerDL has evolved from a site-specific downloader into a **Universal Media Archiver**! Here's what's new:

| Feature | Description |
|---------|-------------|
| 🌍 **1000+ Site Support** | Download from YouTube, Twitter/X, Reddit, TikTok, Instagram, and many more via yt-dlp integration |
| 🖼️ **Gallery Engine** | DeviantArt, Pixiv, ArtStation, and 100+ image gallery sites via gallery-dl |
| 🔄 **Smart Auto-Retry** | Failed downloads automatically retry with exponential backoff |
| 💾 **Crash Recovery** | Resume your downloads even after unexpected shutdowns |
| 🍪 **Browser Cookie Import** | Automatically use your login credentials from Chrome, Firefox, or Edge |
| 📝 **Batch URL Input** | Paste multiple URLs at once for batch downloading (NEW in v2.1!) |
| 🌐 **Proxy Support** | Configure HTTP/HTTPS proxies and custom user agents (NEW in v2.1!) |
| ☁️ **Cloud Ready** | Deploy to Google Cloud with one click using Docker & VNC (NEW!) |

---

## 🎯 Current Features

### Download Capabilities

| Feature | Status | Description |
|---------|--------|-------------|
| **Multi-Site Support** | ✅ Ready | Download from Coomer, Kemono, Erome, Bunkr, SimpCity, jpg5, and 1000+ more sites |
| **Batch URL Input** | ✅ Ready | Paste multiple URLs (one per line) for batch downloading |
| **Multi-Threaded** | ✅ Ready | Faster downloads using multiple simultaneous connections (1-10 threads) |
| **Resume Interrupted Downloads** | ✅ Ready | Continue where you left off if a download is interrupted |
| **Skip Duplicates** | ✅ Ready | Automatically skip files you've already downloaded |
| **Proxy Support** | ✅ Ready | Configure custom proxies in Settings → Network |

### File Types Supported

- 📹 **Videos**: MP4, MKV, WEBM, MOV, AVI, FLV, WMV, M4V
- 🖼️ **Images**: JPG, JPEG, PNG, GIF, BMP, TIFF, WEBP
- 📄 **Documents**: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX
- 📦 **Archives**: ZIP, RAR, 7Z, TAR, GZ

### User Experience

| Feature | Status | Description |
|---------|--------|-------------|
| **6 Languages** | ✅ Ready | English, Spanish, French, Japanese, Russian, Chinese |
| **Dark/Light Theme** | ✅ Ready | Choose your preferred appearance with System auto-detect |
| **Real-Time Progress** | ✅ Ready | See download speed, ETA, and progress for each file |
| **Detailed Logs** | ✅ Ready | Track exactly what's happening during downloads |

### Advanced Features

| Feature | Status | Description |
|---------|--------|-------------|
| **Download Queue Manager** | ✅ Ready | Pause, resume, reorder downloads with persistent queue |
| **Cloud Deployment** | ✅ Ready | Deploy to Google Cloud (or Docker) with full GUI access via browser (VNC) |
| **Cookie Management** | ✅ Ready | Use site cookies for authenticated access |
| **Custom File Naming** | ✅ Ready | 4 different naming schemes to organize your downloads |
| **Folder Organization** | ✅ Ready | Automatically organize downloads by site/user/post |
| **Download History** | ✅ Ready | Browse and search your download history |
| **Bandwidth Limiting** | ✅ Ready | Control download speeds in Settings → Network |
| **File Size Filters** | ✅ Ready | Skip files by size in Settings → Filters |
| **Date Range Filters** | ✅ Ready | Filter by date in Settings → Filters |
| **File Type Exclusions** | ✅ Ready | Exclude specific formats in Settings → Filters |

---

## 🚧 In Development

These features are actively being worked on and will be available soon!

### 🎨 UI Architecture Improvements
**Status: 70% Complete**

Making CoomerDL easier and more pleasant to use:
- ✅ Modular interface components extracted (input, options, log, menu panels)
- ✅ Enhanced progress displays implemented
- ✅ Better notifications and status updates
- 🚧 Further refactoring of main UI controller (in progress)
- 🚧 Complete separation of concerns for maintainability

---

## 📅 Planned Features

### Short-Term (Next 1-3 Months)

#### 🌐 Network Options
- ~~**Proxy Support** - Use HTTP, HTTPS, or custom proxies~~ ✅ **COMPLETED**
- ~~**Bandwidth Limiting** - Cap download speeds to not overwhelm your connection~~ ✅ **COMPLETED**
- ~~**Custom Timeouts** - Configure connection and read timeouts~~ ✅ **COMPLETED**

#### 🔍 Advanced Filtering
- ~~**File Size Filters** - Skip files smaller/larger than specified sizes~~ ✅ **COMPLETED**
- ~~**Date Range Filters** - Download only posts from specific time periods~~ ✅ **COMPLETED**
- ~~**File Type Filters** - More granular control over what gets downloaded~~ ✅ **COMPLETED**

#### ⚙️ Enhanced Settings
- **Settings Profiles** - Save and load different configuration presets
- **Import/Export Settings** - Share your settings between computers
- **Per-Site Settings** - Different configurations for different sites

### Medium-Term (3-6 Months)

#### 📊 Statistics Dashboard
- 📈 Total downloads by site
- 💾 Storage usage tracking
- 📅 Download history graphs
- 🏆 Your most downloaded creators

#### 🔔 Notifications
- 🖥️ Desktop notifications when downloads complete
- 🔊 Optional sound alerts
- 📱 (Future) Mobile push notifications

#### 🗂️ Better Organization
- 📁 Custom folder templates with variables
- 🏷️ Automatic tagging based on content type
- 🔄 Duplicate detection using file hashes

---

## 💡 Future Ideas

These are features we're considering for future versions. Vote for your favorites or suggest new ones!

### 🌟 Quality of Life

| Idea | Description | Complexity |
|------|-------------|------------|
| **System Tray** | Minimize to system tray and show notifications | Medium |
| **Keyboard Shortcuts** | Ctrl+V to paste, Ctrl+Enter to download, etc. | Easy |
| **Download Scheduler** | Schedule downloads for specific times | Medium |
| **Auto-Start** | Option to launch CoomerDL when Windows starts | Easy |
| **Drag & Drop URLs** | Drop URLs directly onto the app window | Easy |

### 🚀 Power User Features

| Idea | Description | Complexity |
|------|-------------|------------|
| **Command Line Interface** | Run downloads from terminal/scripts | Medium |
| **Watch Folders** | Auto-download URLs from files in a folder | Medium |
| **Post-Download Actions** | Move files, run scripts after completion | Medium |
| **API Access** | Integrate CoomerDL with other tools | Hard |
| **Headless Mode** | Run without GUI for servers | Medium |

### 🎨 Interface Enhancements

| Idea | Description | Complexity |
|------|-------------|------------|
| **Thumbnail Previews** | See image previews in download history | Medium |
| **Custom Themes** | Create and share custom color schemes | Medium |
| **Compact Mode** | Minimal UI for small windows | Easy |
| **Multi-Window** | Multiple download windows | Hard |

### 🔧 Site-Specific Features

| Idea | Description | Complexity |
|------|-------------|------------|
| **Favorite Creators** | Track and get notified of new posts | Medium |
| **Creator Search** | Search for creators across supported sites | Medium |
| **Playlist Support** | Download entire YouTube/video playlists | Medium |
| **Gallery Detection** | Auto-detect and download linked galleries | Medium |

### 🛡️ Reliability & Performance

| Idea | Description | Complexity |
|------|-------------|------------|
| **Download Verification** | Verify file integrity after download | Easy |
| **Parallel Album Downloads** | Download multiple albums simultaneously | Medium |
| **Smart Retry** | Different retry strategies per site | Medium |
| **Download Analytics** | Track success rates and speeds | Easy |

### 📱 Platform Expansion

| Idea | Description | Complexity |
|------|-------------|------------|
| **macOS Native** | Native macOS application | Hard |
| **Linux Native** | Native Linux application | Medium |
| **Native Web Interface** | Re-write UI in Flask/React for true headless web support | Very Hard |
| **Mobile App** | iOS/Android companion app | Very Hard |

---

## 🗳️ Feature Requests

### How to Request Features

1. **GitHub**: Open an issue with the "feature request" label
2. **Discussions**: Start a discussion in the GitHub Discussions tab

### Current Top Requests

Based on community feedback, these are the most requested features:

1. 🥇 **Batch URL Input** - *In Development*
2. 🥈 **Download Queue Manager** - *In Development*
3. 🥉 **Proxy Support** - *Planned*
4. 4️⃣ **Bandwidth Limiting** - *Planned*
5. 5️⃣ **Scheduled Downloads** - *Under Consideration*

---

## 📊 Release Timeline

| Version | Expected | Major Features |
|---------|----------|----------------|
| **2.1** | Q1 2025 | Queue Manager, Batch URLs, UI Improvements |
| **2.2** | Q2 2025 | Proxy Support, Bandwidth Limiting, Filters |
| **2.3** | Q3 2025 | Statistics Dashboard, Notifications |
| **3.0** | 2025 | Major UI Overhaul, CLI Mode, API Access |

*Note: Timelines are estimates and may change based on development progress and community feedback.*

---

## 🤝 Contributing

Want to help make CoomerDL better? Here's how:

- **Report Bugs**: Found something broken? Let us know on GitHub!
- **Suggest Features**: Have an idea? We'd love to hear it!
- **Translations**: Help us support more languages
- **Code**: Check out our [Developer Roadmap](DEVELOPMENT_ROADMAP.md) if you want to contribute code

---

## 📣 Stay Updated

- **GitHub**: Watch the repository for release notifications
- **Releases**: Check the [Releases page](https://github.com/primoscope/CoomerDL/releases) for updates

---

*Last updated: December 2024*

*Have feedback on this roadmap? Let us know on Discord or GitHub!*
