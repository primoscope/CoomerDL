# CoomerDL Features Guide

Complete reference for all CoomerDL features.

## Table of Contents

- [Download Features](#download-features)
- [Site Support](#site-support)
- [User Interface](#user-interface)
- [File Management](#file-management)
- [Advanced Features](#advanced-features)
- [Settings](#settings)

---

## Download Features

### Multi-Site Support

CoomerDL supports 1000+ websites through three engines:

1. **Native Scrapers** (Optimized, Fast)
   - Coomer.su/st, Kemono.su/cr
   - Erome.com, Bunkr.io
   - SimpCity.su, Jpg5.su

2. **Universal Engine** (yt-dlp - 1000+ sites)
   - YouTube, Vimeo, Dailymotion
   - Twitter/X, Reddit, Instagram, TikTok
   - And many more...

3. **Gallery Engine** (gallery-dl - 100+ sites)
   - DeviantArt, Pixiv, ArtStation
   - Twitter media, Tumblr

### Batch URL Input

Download from multiple sources at once:

```
https://coomer.su/onlyfans/user/creator1
https://kemono.su/patreon/user/12345
https://erome.com/a/AbCdEf
https://youtube.com/watch?v=...
```

**Features**:
- One URL per line
- Empty lines ignored
- Duplicate URLs filtered
- Invalid URLs highlighted
- Drag & drop text files

### Resume Interrupted Downloads

CoomerDL automatically resumes interrupted downloads:

- Partial files are continued
- Completed files are skipped
- Works across app restarts
- Crash recovery for queued downloads

### Duplicate Detection

Downloaded files are tracked in SQLite database:

- Skip files you've already downloaded
- Fast hash-based duplicate checking
- Prevents wasting bandwidth
- Database caching for performance

### Download Queue System

Manage multiple downloads efficiently:

- Persistent queue across restarts
- Pause/resume individual downloads
- Reorder queue items
- Cancel specific downloads
- View queue history

### File Type Filtering

Choose what to download:

- ✅ **Images**: JPG, PNG, GIF, WEBP, BMP, TIFF
- ✅ **Videos**: MP4, WEBM, MKV, MOV, AVI, FLV
- ✅ **Documents**: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX
- ✅ **Archives**: ZIP, RAR, 7Z, TAR, GZ

### Multi-Threaded Downloads

Configure concurrent downloads (1-10 threads):

- **1-3 threads**: Conservative, gentle on servers
- **4-6 threads**: Balanced (recommended)
- **7-10 threads**: Aggressive, may trigger rate limits

---

## Site Support

### Coomer.su / Kemono.su

**What You Can Download**:
- Full creator profiles
- Individual posts
- All media from a creator

**URL Formats**:
```
https://coomer.su/{service}/user/{username}
https://kemono.su/{service}/user/{user_id}/post/{post_id}
```

**Features**:
- Subdomain failover (n1-n10 mirrors)
- Pagination support
- Cookie authentication for premium content

### Erome.com

**What You Can Download**:
- Albums
- User profiles
- Individual images/videos

**URL Formats**:
```
https://erome.com/a/{album_id}
https://erome.com/{username}
```

### Bunkr.io

**What You Can Download**:
- Image/video galleries
- Direct file links

**Features**:
- Multiple domain support (.io, .si, .sk, etc.)
- Progress notifications

### SimpCity.su

**What You Can Download**:
- Forum thread attachments
- Media from posts

**Features**:
- Requires cookies for access
- Pagination support

### Universal Sites (yt-dlp)

Download from 1000+ sites including:

- **Video**: YouTube, Vimeo, Twitch, DailyMotion
- **Social**: Twitter/X, Reddit, Instagram, TikTok
- **Streaming**: Pornhub, Xvideos, and adult sites
- **And many more...**

**Configuration**:
- Settings → Universal → Enable yt-dlp
- Choose video quality/format
- Metadata embedding options

### Gallery Sites (gallery-dl)

Download from 100+ image galleries:

- **Art**: DeviantArt, Pixiv, ArtStation
- **Social**: Twitter media galleries, Tumblr
- **Image Hosts**: Imgur, Flickr

---

## User Interface

### Modern Multi-Page Design

Navigate between pages:

- **Home**: Main download interface
- **Queue**: View and manage download queue
- **History**: Browse download history
- **Converter**: Media conversion tools
- **Settings**: Application configuration

### Dark/Light Theme

Choose your preferred appearance:

- **Light Theme**: Bright, clear interface
- **Dark Theme**: Easy on the eyes
- **System**: Follows OS preference

### Multi-Language Support

Available languages:

- 🇺🇸 English
- 🇪🇸 Spanish (Español)
- 🇫🇷 French (Français)
- 🇯🇵 Japanese (日本語)
- 🇷🇺 Russian (Русский)
- 🇨🇳 Chinese (中文)

---

## File Management

### Folder Structure Options

Choose how files are organized:

1. **Default**: `site/username/post-id/file.ext`
2. **Flat**: `username/file.ext`
3. **By Date**: `site/YYYY-MM-DD/file.ext`
4. **Custom**: Define your own template

### File Naming Modes

Four naming conventions:

1. **Original**: Keep original filename
2. **Numbered**: Sequential (001.jpg, 002.jpg)
3. **Timestamped**: Include download timestamp
4. **Hash-based**: Use content hash (prevents duplicates)

### Download History

Track all downloads in searchable database:

- View all downloaded files
- Search by URL, filename, or date
- Filter by site or file type
- Export history to CSV/JSON
- Re-download from history

---

## Advanced Features

### Cookie Authentication

Access private or premium content:

**Manual Method**:
1. Export cookies from browser (using EditThisCookie extension)
2. Settings → Cookies → Import
3. Select site and paste cookies

**Auto-Import Method**:
1. Settings → Universal → Browser Cookie Import
2. Choose browser (Chrome, Firefox, Edge)
3. Cookies automatically imported

### Proxy Support

Route downloads through a proxy:

**Configuration**:
1. Settings → Network → Enable Proxy
2. Enter proxy URL: `http://proxy:port` or `socks5://proxy:port`
3. Optional: Username/password

**Use Cases**:
- Bypass regional restrictions
- Privacy/anonymity
- Corporate network requirements

### Bandwidth Limiting

Control download speed:

1. Settings → Network → Bandwidth Limit
2. Set max speed in KB/s (0 = unlimited)
3. Prevents network saturation

### Advanced Filters

Filter downloads by:

**File Size**:
- Min size: Skip small files (thumbnails)
- Max size: Skip large files

**Date Range**:
- Download only posts from specific dates
- Format: YYYY-MM-DD

**Custom Patterns**:
- Include/exclude by filename pattern
- Regex support

### Scheduled Downloads

Schedule downloads for specific times:

1. Menu → Scheduled Downloads
2. Click "New Schedule"
3. Configure:
   - **Once**: Run at specific date/time
   - **Daily**: Run every day at specific time
   - **Weekly**: Run weekly on specific day
   - **Interval**: Run every X minutes

**Use Cases**:
- Download during off-peak hours
- Regular profile checks
- Automated archiving

---

## Settings

### General Settings

- **Language**: Change interface language
- **Theme**: Light/Dark/System
- **Auto-Update**: Check for updates on startup

### Download Settings

- **Max Downloads**: Simultaneous downloads (1-10)
- **Folder Structure**: How to organize files
- **File Naming**: Naming convention
- **Retries**: Number of retry attempts
- **Timeout**: Connection timeout (seconds)

### Network Settings

- **Proxy**: HTTP/SOCKS proxy configuration
- **Bandwidth Limit**: Max download speed
- **User-Agent**: Custom user agent string
- **Rate Limiting**: Requests per second

### Universal (yt-dlp) Settings

- **Enable**: Use yt-dlp for supported sites
- **Quality**: Video quality preference
- **Format**: Preferred container format
- **Metadata**: Embed metadata in files
- **Cookies**: Import browser cookies

### Gallery (gallery-dl) Settings

- **Enable**: Use gallery-dl for galleries
- **Quality**: Image quality
- **Metadata**: Download metadata files

### Filter Settings

- **File Size**: Min/max file size
- **Date Range**: Post date filters
- **File Types**: Enable/disable file types
- **Patterns**: Include/exclude patterns

### Logging Settings

- **Log Level**: Debug/Info/Warning/Error
- **Log File**: Save logs to file
- **Max Log Size**: Log rotation size

---

## Tips & Tricks

### Performance Optimization

1. **Reduce Threads**: Lower threads = more stable
2. **Bandwidth Limit**: Prevent network saturation
3. **Filter by Size**: Skip small thumbnails
4. **Use Batch Mode**: More efficient than one-by-one

### Accessing Private Content

1. **Export Cookies**: Use browser extension
2. **Import to CoomerDL**: Settings → Cookies
3. **Auto-Import**: Settings → Universal → Browser Cookies

### Avoiding Rate Limits

1. **Lower Thread Count**: Use 3-5 threads max
2. **Add Delays**: Settings → Network → Rate Limiting
3. **Use Proxy**: Rotate IP addresses
4. **Schedule Off-Peak**: Night/early morning downloads

### Organizing Downloads

1. **Custom Folders**: Settings → Structure
2. **File Naming**: Choose meaningful names
3. **Tags**: Use options dictionary for metadata
4. **History**: Track what you've downloaded

---

For more help, see:
- [Getting Started](GETTING_STARTED.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [FAQ](FAQ.md)
