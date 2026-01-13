![Windows Compatibility](https://img.shields.io/badge/Windows-10%2C%2011-blue)
![Downloads](https://img.shields.io/github/downloads/primoscope/CoomerDL/total)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

# CoomerDL - Universal Media Archiver 🎬

> **Download media from 1000+ websites with a simple, user-friendly desktop application**

CoomerDL is a powerful Python desktop application for downloading images, videos, and galleries from over 1000 websites. Whether you're archiving content from YouTube, Twitter, DeviantArt, or specialized sites, CoomerDL handles it all with smart automation and an intuitive interface.

[![Download Latest Release](https://img.shields.io/badge/Download-Latest%20Release-brightgreen?style=for-the-badge)](https://github.com/primoscope/CoomerDL/releases)

---

## ✨ Key Features

### 🌐 Universal Support
- **1000+ Websites Supported** - YouTube, Twitter/X, Reddit, TikTok, Instagram, and more
- **Specialized High-Speed Scrapers** - Optimized for Coomer, Kemono, Erome, Bunkr, SimpCity, jpg5
- **Gallery Support** - DeviantArt, Pixiv, ArtStation, and 100+ image gallery sites
- **Smart URL Detection** - Automatically uses the best downloader for each URL

### 🚀 Powerful Automation
- **Batch Downloads** - Paste multiple URLs and download them all at once
- **Auto-Retry** - Failed downloads automatically retry with smart backoff
- **Crash Recovery** - Resume interrupted downloads after restart
- **Duplicate Detection** - Automatically skip files you've already downloaded
- **Rate Limiting** - Respectful download speeds to avoid getting blocked

### 🎨 User-Friendly Interface
- **Modern GUI** - Clean, intuitive interface with light and dark themes
- **Real-Time Progress** - See download speed, progress, and estimated time
- **Multi-Language** - Available in 6 languages: English, Spanish, French, Japanese, Russian, and Chinese
- **Queue Management** - Organize, prioritize, and control your downloads
- **Download History** - Browse and search everything you've downloaded

### ⚙️ Advanced Configuration
- **Proxy Support** - Use HTTP/HTTPS/SOCKS proxies (NEW!)
- **Custom User Agent** - Customize your browser identity
- **File Filtering** - Choose which file types to download
- **Format Selection** - Pick video quality and audio formats
- **Cookie Import** - Auto-authenticate using your browser cookies
- **FFmpeg Integration** - Merge video/audio, convert formats, embed metadata

---

## 🎯 Supported Sites

CoomerDL supports **1000+ websites** through three powerful engines:

### 🏎️ Native Scrapers (Optimized for Speed)
High-performance, purpose-built downloaders for these popular sites:
- **[coomer.su](https://coomer.su/)** - Patreon, OnlyFans, and other content creators
- **[kemono.su](https://kemono.su/)** - Similar to Coomer with additional platforms
- **[erome.com](https://www.erome.com/)** - Image and video albums
- **[bunkr-albums.io](https://bunkr-albums.io/)** - File hosting and albums
- **[simpcity.su](https://simpcity.su/)** - Forum media downloads
- **[jpg5.su](https://jpg5.su/)** - Image hosting

### 🎬 Video Sites (via yt-dlp)
Download from **1000+ video platforms** including:
- **Streaming**: YouTube, Vimeo, Dailymotion, Twitch
- **Social Media**: Twitter/X, Reddit, TikTok, Instagram, Facebook
- **And many more**: [View full list](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

### 🖼️ Image Galleries (via gallery-dl)
Support for **100+ image gallery sites** including:
- **Art Platforms**: DeviantArt, Pixiv, ArtStation
- **Social**: Tumblr, Pinterest, Instagram
- **Image Boards**: Various supported boards
- **And more**: [View full list](https://github.com/mikf/gallery-dl/blob/master/docs/supportedsites.md)

---

## 📥 Quick Start

### For Windows Users (Easiest)
1. Download the latest `CoomerDL-Windows.zip` from [Releases](https://github.com/primoscope/CoomerDL/releases)
2. Extract the ZIP file to a folder
3. Double-click `CoomerDL.exe` to launch - that's it!

> **Note**: Windows may show a SmartScreen warning for unsigned executables. Click "More info" → "Run anyway" to proceed.

### For Python Users
1. **Install Python 3.8+** ([Download Python](https://www.python.org/downloads/))
2. **Install FFmpeg** (Optional, for video merging):
   - Windows: `winget install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`
3. **Clone and run**:
   ```bash
   git clone https://github.com/primoscope/CoomerDL.git
   cd CoomerDL
   pip install -r requirements.txt
   python main.py
   ```

> 💡 **Linux users**: You may need to install tkinter: `sudo apt install python3-tk`

---

## 🎮 How to Use

1. **Launch CoomerDL** - The application window will open
2. **Paste URLs** - Enter one or more URLs (one per line for batch downloads)
3. **Choose Options** - Select what to download (images, videos, etc.)
4. **Click Download** - Sit back and watch the magic happen!

![Usage Demo](https://github.com/primoscope/CoomerDL/blob/main/resources/screenshots/0627.gif)

### Pro Tips
- 📝 **Batch Downloads**: Paste multiple URLs (one per line) to download them all at once
- 🌐 **Proxy Configuration**: Go to Settings → Network to configure proxy settings
- 🍪 **Cookie Import**: Settings → Universal → Import cookies from your browser for authenticated downloads
- 📋 **Queue Management**: Click the Queue button to manage, reorder, and control your downloads
- ⚙️ **Custom Filters**: Use Settings → Downloads to configure file type filters and download options

---

## 🌍 Language Support & Community

### Supported Languages
CoomerDL is available in 6 languages:  
🇺🇸 English | 🇪🇸 Español | 🇫🇷 Français | 🇯🇵 日本語 | 🇨🇳 中文 | 🇷🇺 Русский

### Command-Line Alternatives
Prefer CLI tools? Check out other similar command-line tools for specific sites.

---

---

## ⚠️ Troubleshooting

### Common Issues

<details>
<summary><b>ModuleNotFoundError: No module named 'tkinter'</b></summary>

**Linux users need to install tkinter separately:**
```bash
sudo apt install python3-tk      # Ubuntu/Debian
sudo dnf install python3-tkinter # Fedora
sudo pacman -S tk               # Arch Linux
```

**Windows/macOS:** Reinstall Python from [python.org](https://www.python.org/downloads/) with tkinter enabled.
</details>

<details>
<summary><b>Missing Python packages</b></summary>

Update or reinstall dependencies:
```bash
pip install -r requirements.txt --upgrade
# or force reinstall
pip install -r requirements.txt --force-reinstall
```
</details>

<details>
<summary><b>FFmpeg not found</b></summary>

Install FFmpeg for video/audio merging:
- **Windows:** `winget install ffmpeg`
- **macOS:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`

Verify: `ffmpeg -version`

Note: CoomerDL works without FFmpeg, but video merging won't be available.
</details>

<details>
<summary><b>Downloads fail with 403/429 errors</b></summary>

- **403 Forbidden:** Site requires authentication. Use Settings → Universal → Import browser cookies.
- **429 Too Many Requests:** Rate limited. Lower concurrent downloads in Settings → Network.
</details>

<details>
<summary><b>YouTube or other site downloads fail</b></summary>

If you get "invalid URL" or "not supported" errors:
- **Verify yt-dlp is installed:** `pip install -U yt-dlp`
- **Check network connectivity** to the target site
- **For video+audio merging,** install FFmpeg (see installation section above)
- **Try updating yt-dlp:** `pip install --upgrade yt-dlp`
- **Check the URL format** - some sites require specific URL patterns

**Testing yt-dlp directly:**
```bash
# Test if yt-dlp can handle the URL
yt-dlp --list-formats YOUR_URL

# Download with yt-dlp directly
yt-dlp -f best YOUR_URL
```

Note: CoomerDL uses yt-dlp which supports 1000+ sites including YouTube, Twitter, TikTok, etc.
</details>

<details>
<summary><b>Application won't start or crashes</b></summary>

Check for common issues:
- **Python version:** Requires Python 3.8 or higher - check with `python --version`
- **Missing dependencies:** Run `pip install -r requirements.txt` to reinstall all packages
- **Tkinter missing (Linux):** Install with `sudo apt install python3-tk`
- **Corrupted settings:** Delete the settings file in the app data directory and restart
</details>

<details>
<summary><b>High memory usage or database locked</b></summary>

- Lower concurrent downloads in settings
- Clear completed downloads from queue
- Close other CoomerDL instances (only one should run)
- Restart the application periodically
</details>

### Still Need Help?

1. Check [existing issues](https://github.com/primoscope/CoomerDL/issues)
2. Create a [new issue](https://github.com/primoscope/CoomerDL/issues/new) with:
   - Python version (`python --version`)
   - OS and version
   - Full error message
   - Steps to reproduce

---

---

## 👨‍💻 For Developers

### Contributing
Contributions are welcome! This project is optimized for both human developers and AI coding agents.

**Documentation for Developers:**
- [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) - Technical roadmap with task breakdowns
- [TASKS.md](TASKS.md) - Detailed task definitions with acceptance criteria
- [SPECIFICATIONS.md](SPECIFICATIONS.md) - Code specifications for new features
- [tests/CONTRACTS.md](tests/CONTRACTS.md) - System behavior contracts

### Running Tests
```bash
pytest tests/         # Run all 241 tests
pytest tests/ -v      # Verbose output
python main.py        # Manual testing
```

### Tech Stack
- **UI:** CustomTkinter (modern tkinter framework)
- **Backend:** Python 3.8+ with threading
- **Engines:** yt-dlp, gallery-dl, custom scrapers
- **Database:** SQLite for history and caching
- **HTTP:** requests with connection pooling

### Architecture Highlights
- **Multi-Engine System:** Native scrapers, yt-dlp adapter, gallery-dl adapter with smart routing
- **Event-Driven:** Backend emits events, UI subscribes (no tight coupling)
- **Job Queue:** Persistent queue with crash recovery and status tracking
- **Rate Limiting:** Per-domain concurrency caps and request throttling
- **Thread-Safe:** Event-based cancellation, locked database access

### Quick Start for Development
```bash
git clone https://github.com/primoscope/CoomerDL.git
cd CoomerDL
pip install -r requirements.txt
pip install pytest  # For running tests
python main.py      # Run the application
```

### Building Executables

Want to build your own executable? See [BUILDING.md](BUILDING.md) for detailed instructions.

**Quick build:**
```bash
pip install pyinstaller
python build.py
```

The executable will be in the `dist/` folder.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⭐ Support the Project

If you find CoomerDL useful, please consider:
- ⭐ **Star this repository** on GitHub
- 🐛 **Report bugs** and suggest features
- 🤝 **Contribute** to the project

Your support helps maintain and improve CoomerDL!

---

**Made with ❤️ by the CoomerDL community**
