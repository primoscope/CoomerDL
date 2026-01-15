# Frequently Asked Questions (FAQ)

Quick answers to common questions about CoomerDL.

## General Questions

### What is CoomerDL?

CoomerDL is a universal media downloader that supports 1000+ websites including Coomer, Kemono, YouTube, Twitter/X, Reddit, and many more. It provides a desktop application for batch downloading media files.

### Is CoomerDL free?

Yes! CoomerDL is completely free and open-source under the MIT license.

### Is CoomerDL safe?

Yes. The source code is publicly available on GitHub. Windows Defender may flag it as the application is unsigned (common for open-source software), but it's a false positive.

### What operating systems are supported?

- Windows 10/11
- macOS 10.14+
- Linux (any distribution with Python 3.8+)

### Do I need to install anything else?

Basic functionality works out of the box. Optional:
- **FFmpeg**: For video conversion (auto-detected)
- **Python 3.8+**: If running from source

---

## Download Questions

### What sites does CoomerDL support?

**Native Support** (Optimized):
- Coomer.su/st, Kemono.su/cr
- Erome.com, Bunkr.io
- SimpCity.su, Jpg5.su

**Universal Support** (via yt-dlp):
- 1000+ sites including YouTube, Twitter/X, Reddit, Instagram, TikTok, etc.

**Gallery Support** (via gallery-dl):
- 100+ image gallery sites including DeviantArt, Pixiv, ArtStation

### Can I download from multiple URLs at once?

Yes! Use batch URL input:
1. Paste multiple URLs (one per line) in the URL box
2. Or drag & drop a text file with URLs

### Can I download private/premium content?

Yes, by importing cookies from your browser:

**Method 1**: Manual import
1. Login to site in browser
2. Export cookies using EditThisCookie extension
3. Settings → Cookies → Import

**Method 2**: Auto-import
1. Login to site in browser
2. Settings → Universal → Browser Cookie Import

### How do I download an entire profile?

Paste the profile URL:
```
https://coomer.su/onlyfans/user/username
https://kemono.su/patreon/user/12345
```

CoomerDL will automatically fetch all posts and media.

### Why are some files skipped?

Files are skipped if:
- Already downloaded (duplicate detection)
- File type is disabled (Images/Videos/Docs/Archives checkboxes)
- Filtered out by size/date filters
- File no longer exists on server

### Can downloads be resumed?

Yes! CoomerDL automatically resumes:
- Interrupted downloads
- After application restart
- After system crash

Just start the download again - it will skip completed files and resume partial files.

---

## Technical Questions

### Where are files saved?

Files are saved to the folder you select with "Select Folder". Default structure:
```
YourFolder/
  └── site-name/
      └── username/
          └── post-id/
              ├── file1.jpg
              └── file2.mp4
```

Change structure in: Settings → Downloads → Folder Structure

### Where is the database stored?

Download history and settings are stored in:
```
resources/config/downloads.db     (download history)
resources/config/settings.json    (application settings)
resources/config/scheduler.db     (scheduled downloads)
```

### How do I backup my settings?

Copy these files:
```
resources/config/settings.json    (settings)
resources/config/downloads.db     (history)
resources/config/cookies/         (authentication cookies)
```

Restore by copying them back to a fresh installation.

### How much disk space do I need?

Varies by content:
- **Images**: 1-5 MB per image
- **Videos**: 10-500 MB per video
- **Profiles**: 100 MB to 100+ GB

Always ensure several GB of free space before starting large downloads.

### Can I run multiple instances?

Not recommended. Multiple instances may:
- Conflict over database access
- Duplicate downloads
- Cause rate limiting

Use batch URL mode instead for multiple downloads.

---

## Performance Questions

### How many simultaneous downloads should I use?

**Recommended**: 3-5 threads

- **1-3**: Conservative, gentle on servers
- **4-6**: Balanced (best for most users)
- **7-10**: Aggressive, may trigger rate limits

Adjust in: Settings → Downloads → Max Downloads

### Why are downloads slow?

Common causes:
1. **Bandwidth limit**: Check Settings → Network → Bandwidth Limit
2. **Too few threads**: Increase max downloads to 5-7
3. **Server throttling**: Site is limiting speed
4. **Network congestion**: Try different time/day
5. **Proxy overhead**: Proxies add latency

### How do I speed up downloads?

1. **Increase threads**: Settings → Max Downloads → 5-7
2. **Remove bandwidth limit**: Settings → Network → 0 (unlimited)
3. **Use wired connection**: Ethernet is faster than WiFi
4. **Download off-peak**: Night/early morning
5. **Disable unnecessary filters**: Download all file types

### Why is the application using a lot of CPU/RAM?

Common causes:
1. **Too many threads**: Reduce to 3-5
2. **Large files**: Video processing requires resources
3. **Memory leak**: Restart application

Solutions:
- Lower thread count
- Close other applications
- Restart CoomerDL periodically

---

## Authentication Questions

### How do I access private content?

Import cookies from your browser:

1. **Manual Method**:
   - Login to site in browser
   - Export cookies (EditThisCookie extension)
   - Settings → Cookies → Import

2. **Auto Method**:
   - Login to site in browser
   - Settings → Universal → Browser Cookie Import
   - Select browser

### Do I need to re-import cookies?

Yes, periodically:
- Cookies expire (usually weeks/months)
- After logout from site
- If downloads start failing

Signs cookies expired:
- "Access denied" errors
- "Login required" messages
- 403 Forbidden errors

### Are my cookies safe?

Cookies are stored locally on your computer in:
```
resources/config/cookies/
```

They are **not** sent anywhere except to the sites you're downloading from.

**Security tips**:
- Don't share cookie files
- Keep CoomerDL updated
- Don't use on public computers

---

## Error Questions

### "No files found" - What do I do?

1. **Verify URL**: Open in browser, confirm media exists
2. **Check authentication**: Private content needs cookies
3. **Try different URL**: Post URL vs profile URL
4. **Enable universal mode**: Settings → Universal → Enable yt-dlp

### "Download failed" - How do I fix it?

1. **Check internet**: Test connection
2. **Reduce threads**: Lower to 3 max downloads
3. **Wait and retry**: Temporary site issues
4. **Check logs**: View error messages
5. **Update CoomerDL**: Ensure latest version

### "Access denied" / "403 Forbidden" - What now?

1. **Import cookies**: Site requires authentication
2. **Change user-agent**: Settings → Network → User-Agent
3. **Use proxy**: Settings → Network → Proxy
4. **Wait**: Rate limit expires in 15-60 minutes

### "FFmpeg not found" - Do I need it?

FFmpeg is optional but recommended for:
- Video format conversion
- Audio extraction
- Metadata embedding

**Install**:
- **Windows**: Download from ffmpeg.org
- **macOS**: `brew install ffmpeg`
- **Linux**: `apt install ffmpeg` or `dnf install ffmpeg`

Without FFmpeg, you can still download but can't convert formats.

---

## Feature Questions

### Can I schedule downloads?

Yes! Use the scheduler:
1. Menu → Scheduled Downloads
2. Click "New Schedule"
3. Configure time/frequency
4. Save

Schedules persist across restarts.

### Can I filter downloads?

Yes! Multiple filter options:

**File Type**: Enable/disable Images/Videos/Docs/Archives

**File Size**: Settings → Filters → Min/Max size

**Date Range**: Settings → Filters → Date range

**Patterns**: Settings → Filters → Include/exclude patterns

### Can I use a proxy?

Yes!
1. Settings → Network → Enable Proxy
2. Enter proxy URL:
   - HTTP: `http://proxy:port`
   - SOCKS5: `socks5://proxy:port`
3. Optional: Username/password

### Can I limit download speed?

Yes!
1. Settings → Network → Bandwidth Limit
2. Set max speed in KB/s
3. 0 = unlimited

### Can I organize files differently?

Yes! Multiple organization options:

**Folder Structure**: Settings → Downloads → Folder Structure
- Default: site/user/post/files
- Flat: user/files
- By date: site/YYYY-MM-DD/files
- Custom: Your own template

**File Naming**: Settings → Downloads → File Naming Mode
- Original: Keep original name
- Numbered: Sequential (001, 002, ...)
- Timestamped: Include timestamp
- Hash-based: Content hash

---

## Legal Questions

### Is downloading from these sites legal?

**Disclaimer**: Legal status varies by country and content. CoomerDL is a tool; you are responsible for how you use it.

**General guidelines**:
- ✅ Downloading your own content: Legal
- ✅ Downloading public domain content: Legal
- ⚠️ Downloading copyrighted content: Depends on jurisdiction and fair use
- ❌ Redistributing copyrighted content: Usually illegal

Consult local laws and site terms of service.

### Can I get banned for using CoomerDL?

Possible but rare. To minimize risk:
- Use reasonable thread counts (3-5)
- Add delays between requests
- Don't abuse rate limits
- Use cookies (looks like browser)
- Respect robots.txt

### Can I redistribute CoomerDL?

Yes! Under MIT license you can:
- Use for personal/commercial purposes
- Modify the source code
- Distribute original or modified versions

Must include original license and copyright notice.

---

## Troubleshooting

### Application won't start

**Windows**:
- Right-click → Run as Administrator
- Check Windows Defender didn't quarantine it
- Install Visual C++ Redistributable

**macOS**:
- Right-click → Open (first time only)
- Grant permissions in System Preferences → Security

**Linux**:
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (need 3.8+)

### Nothing happens when I click Download

1. **Check URL**: Must be valid URL from supported site
2. **Select folder**: Must choose download folder
3. **Check logs**: Look for error messages
4. **Restart**: Close and reopen application

### Downloads stop randomly

1. **Check connection**: Internet stable?
2. **Check disk space**: Enough free space?
3. **Reduce threads**: Lower to 3
4. **Check rate limits**: Wait and retry

---

## Support

### Where can I get help?

1. **Documentation**: Read [Getting Started](GETTING_STARTED.md) and [Troubleshooting](TROUBLESHOOTING.md)
2. **GitHub Issues**: Search existing issues
3. **New Issue**: Open detailed bug report
4. **Discussions**: Community Q&A

### How do I report a bug?

1. Go to [GitHub Issues](https://github.com/primoscope/CoomerDL/issues)
2. Search if already reported
3. If new, click "New Issue"
4. Include:
   - Operating system
   - CoomerDL version
   - Steps to reproduce
   - Error message/logs
   - Expected vs actual behavior

### How do I request a feature?

1. Check [Roadmap](../../docs/planning/ROADMAP.md) if already planned
2. Search [GitHub Issues](https://github.com/primoscope/CoomerDL/issues)
3. Open new issue with "Feature Request" label
4. Describe use case and benefits

### How can I contribute?

- **Code**: Fork, make changes, submit pull request
- **Translations**: Help translate to more languages
- **Documentation**: Improve guides and docs
- **Bug Reports**: Test and report issues
- **Feedback**: Suggest improvements

---

**Didn't find your answer?** Open an issue on GitHub!
