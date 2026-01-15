# Troubleshooting Guide

Solutions to common CoomerDL problems.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Download Problems](#download-problems)
- [Performance Issues](#performance-issues)
- [Authentication Issues](#authentication-issues)
- [Error Messages](#error-messages)

---

## Installation Issues

### Windows: "Windows protected your PC"

**Problem**: SmartScreen blocks the application.

**Solution**:
1. Click "More info"
2. Click "Run anyway"
3. Or add exception in Windows Defender

This is a false positive due to the app being unsigned.

### macOS: "Cannot be opened because the developer cannot be verified"

**Problem**: macOS Gatekeeper blocks unsigned apps.

**Solution**:
1. Right-click the app
2. Select "Open"
3. Click "Open" in the dialog
4. Grant permissions if prompted

### Linux: Missing dependencies

**Problem**: `ModuleNotFoundError` or missing libraries.

**Solution**:
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install system dependencies (Ubuntu/Debian)
sudo apt install python3-tk ffmpeg

# Install system dependencies (Fedora)
sudo dnf install python3-tkinter ffmpeg
```

---

## Download Problems

### "No files found"

**Possible Causes**:
- URL doesn't contain media
- Page requires authentication
- Site not supported
- URL format incorrect

**Solutions**:

1. **Verify URL**:
   - Open URL in browser
   - Confirm media exists
   - Check URL format

2. **Check Authentication**:
   - Private content needs cookies
   - Settings → Cookies → Import browser cookies

3. **Try Different URL**:
   - Profile URL instead of post URL
   - Or vice versa

4. **Enable Universal Mode**:
   - Settings → Universal → Enable yt-dlp
   - Supports 1000+ additional sites

### "Download failed" / "Connection error"

**Possible Causes**:
- No internet connection
- Site is down
- Rate limiting
- Firewall/antivirus blocking

**Solutions**:

1. **Check Connection**:
   ```bash
   # Test internet
   ping google.com
   
   # Test specific site
   curl -I https://coomer.su
   ```

2. **Reduce Threads**:
   - Settings → Downloads → Max Downloads → 3
   - Too many requests trigger rate limits

3. **Add Delay**:
   - Settings → Network → Rate Limiting
   - Add delays between requests

4. **Check Firewall**:
   - Allow CoomerDL through firewall
   - Check antivirus isn't blocking

5. **Use Proxy**:
   - Settings → Network → Proxy
   - Route through different IP

### Files incomplete or corrupted

**Possible Causes**:
- Download interrupted
- Connection unstable
- Disk space full

**Solutions**:

1. **Delete Incomplete Files**:
   - Remove .part or .tmp files
   - CoomerDL will re-download

2. **Check Disk Space**:
   ```bash
   # Windows
   dir /s
   
   # Linux/Mac
   df -h
   ```

3. **Resume Download**:
   - CoomerDL automatically resumes
   - Delete database cache if stuck:
     ```
     resources/config/downloads.db
     ```

4. **Stable Connection**:
   - Use wired ethernet instead of WiFi
   - Close bandwidth-heavy applications

### "Access denied" / "403 Forbidden"

**Possible Causes**:
- Site blocks automated downloads
- IP address rate limited
- Cookies expired
- User-agent blocked

**Solutions**:

1. **Import Fresh Cookies**:
   - Settings → Cookies → Import
   - Use EditThisCookie browser extension
   - Export and import new cookies

2. **Change User-Agent**:
   - Settings → Network → User-Agent
   - Copy from browser:
     - Chrome: F12 → Network → Look for User-Agent header
     - Firefox: about:config → general.useragent.override

3. **Use Proxy**:
   - Settings → Network → Proxy
   - Get fresh IP address

4. **Wait and Retry**:
   - Rate limits are temporary
   - Wait 15-60 minutes
   - Try again with lower threads

---

## Performance Issues

### Application slow or freezing

**Possible Causes**:
- Too many simultaneous downloads
- Large files being processed
- Low system resources
- Database cache too large

**Solutions**:

1. **Reduce Threads**:
   - Settings → Downloads → Max Downloads → 3
   - Fewer threads = more stable

2. **Clear Database Cache**:
   ```bash
   # Backup first
   cp resources/config/downloads.db downloads.db.backup
   
   # Then delete
   rm resources/config/downloads.db
   ```

3. **Close Other Apps**:
   - Free up RAM
   - Close browser tabs
   - Stop other downloads

4. **Increase System Resources**:
   - Close background applications
   - Restart computer
   - Check Task Manager/Activity Monitor

### Downloads very slow

**Possible Causes**:
- Bandwidth limit set
- Server throttling
- Network congestion
- Too few threads

**Solutions**:

1. **Check Bandwidth Limit**:
   - Settings → Network → Bandwidth Limit
   - Set to 0 (unlimited) if too low

2. **Increase Threads**:
   - Settings → Downloads → Max Downloads → 5-7
   - More threads = faster (but may trigger limits)

3. **Check Network**:
   - Speed test: https://speedtest.net
   - Use wired connection
   - Close other network apps

4. **Try Different Time**:
   - Download during off-peak hours
   - Night/early morning usually faster

### High CPU/Memory usage

**Possible Causes**:
- Too many concurrent downloads
- Large video processing
- Memory leak

**Solutions**:

1. **Reduce Threads**:
   - Lower max downloads to 3

2. **Restart Application**:
   - Close and reopen CoomerDL
   - Clears memory

3. **Disable Features**:
   - Disable metadata embedding
   - Disable file conversion

---

## Authentication Issues

### "Login required" / "Private content"

**Problem**: Content requires authentication.

**Solution**:

**Method 1: Manual Cookie Import**

1. Install browser extension:
   - Chrome: EditThisCookie
   - Firefox: Cookie Quick Manager

2. Login to site in browser

3. Export cookies from extension

4. CoomerDL:
   - Settings → Cookies
   - Select site
   - Paste exported cookies
   - Save

**Method 2: Auto Cookie Import**

1. Login to site in browser

2. CoomerDL:
   - Settings → Universal
   - Browser Cookie Import
   - Select your browser
   - Cookies auto-imported

### Cookies not working

**Possible Causes**:
- Cookies expired
- Wrong cookie format
- Browser session ended

**Solutions**:

1. **Fresh Login**:
   - Logout from site
   - Login again in browser
   - Export new cookies

2. **Check Cookie Format**:
   - Should be JSON
   - Check for syntax errors
   - Validate JSON: https://jsonlint.com

3. **Stay Logged In**:
   - Keep browser open
   - Don't logout from site
   - Refresh cookies weekly

---

## Error Messages

### "No module named 'yt_dlp'"

**Problem**: yt-dlp not installed.

**Solution**:
```bash
pip install yt-dlp
```

Or reinstall all dependencies:
```bash
pip install -r requirements.txt
```

### "FFmpeg not found"

**Problem**: FFmpeg not installed (needed for video processing).

**Solution**:

**Windows**:
1. Download: https://ffmpeg.org/download.html
2. Extract to C:\ffmpeg
3. Add to PATH or place ffmpeg.exe in CoomerDL folder

**macOS**:
```bash
brew install ffmpeg
```

**Linux**:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

### "Database is locked"

**Problem**: Another instance accessing database.

**Solution**:
1. Close all CoomerDL instances
2. Wait 10 seconds
3. Restart CoomerDL

If persists:
```bash
# Backup database
cp resources/config/downloads.db downloads.db.backup

# Remove lock (if exists)
rm resources/config/downloads.db-journal
```

### "Disk full" / "No space left on device"

**Problem**: Not enough disk space.

**Solution**:
1. Free up space:
   - Delete old downloads
   - Empty recycle bin/trash
   - Move files to external drive

2. Select different folder:
   - Click "Select Folder"
   - Choose drive with more space

3. Check space before download:
   - Large profiles can be 10GB+
   - Ensure adequate space

---

## Getting More Help

If your issue isn't covered here:

1. **Check FAQ**: [FAQ.md](FAQ.md)
2. **Search Issues**: [GitHub Issues](https://github.com/primoscope/CoomerDL/issues)
3. **Open New Issue**: Include:
   - Operating system
   - CoomerDL version
   - Error message (full text)
   - Steps to reproduce
   - Log file (if applicable)

### Providing Logs

Help us help you - include logs:

1. Enable debug logging:
   - Settings → Logging → Log Level → Debug

2. Reproduce the issue

3. Copy log from log panel:
   - Right-click → Select All
   - Right-click → Copy

4. Or find log file:
   ```
   resources/config/logs/coomerdl.log
   ```

5. Include in issue report (remove sensitive data)

---

**Still stuck?** Open an issue on GitHub with detailed information and logs!
