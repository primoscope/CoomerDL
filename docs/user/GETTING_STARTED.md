# Getting Started with CoomerDL

Welcome to CoomerDL! This guide will help you get started with downloading media from your favorite sites.

## Table of Contents

- [Installation](#installation)
- [First Launch](#first-launch)
- [Basic Usage](#basic-usage)
- [Understanding the Interface](#understanding-the-interface)
- [Your First Download](#your-first-download)
- [Next Steps](#next-steps)

---

## Installation

### Windows

1. Download the latest release from [GitHub Releases](https://github.com/primoscope/CoomerDL/releases)
2. Extract the ZIP file to a folder of your choice
3. Run `CoomerDL.exe`

**Note**: Windows Defender or antivirus software may flag the application. This is a false positive due to the application being unsigned. You can safely add an exception.

### macOS

1. Download the latest macOS release
2. Extract the archive
3. Move CoomerDL to your Applications folder
4. Right-click and select "Open" the first time (macOS Gatekeeper)

### Linux

1. Download the Linux release or clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

### From Source

For the latest development version:

```bash
# Clone the repository
git clone https://github.com/primoscope/CoomerDL.git
cd CoomerDL

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

---

## First Launch

### Initial Setup

When you first launch CoomerDL, you'll see the main window with:

1. **URL Input Area** - Where you paste links to download
2. **Download Options** - Choose what types of files to download
3. **Folder Selection** - Pick where to save your downloads
4. **Log Panel** - See what's happening during downloads

### Selecting a Download Folder

Before your first download:

1. Click the **"Select Folder"** button
2. Choose a folder where you want downloads saved
3. The path will be displayed below the URL input

**Tip**: Choose a folder with plenty of free space. Some profiles can contain hundreds or thousands of files!

### Optional: Configure Settings

Click **Settings** in the menu to customize:

- **Language**: Choose from English, Spanish, French, Japanese, Russian, or Chinese
- **Theme**: Light, Dark, or System (follows your OS theme)
- **Downloads**: Number of simultaneous downloads (1-10 threads)
- **Folder Structure**: How files are organized
- **File Naming**: Naming convention for downloaded files

---

## Basic Usage

### Supported Sites

CoomerDL supports downloading from:

#### Native Support (Optimized)
- **Coomer.su / Coomer.st** - Creator profiles and posts
- **Kemono.su / Kemono.cr** - Creator profiles and posts  
- **Erome.com** - Albums and profiles
- **Bunkr.io** - Image/video galleries
- **SimpCity.su** - Forum threads with media
- **Jpg5.su** - Image galleries

#### Universal Support (1000+ Sites via yt-dlp)
- YouTube, Vimeo, Dailymotion
- Twitter/X, Reddit, Instagram, TikTok
- And many more...

#### Gallery Support (100+ Sites via gallery-dl)
- DeviantArt, Pixiv, ArtStation
- Twitter media galleries
- And many more...

### What Gets Downloaded

By default, CoomerDL downloads:
- ✅ Images (JPG, PNG, GIF, WEBP, etc.)
- ✅ Videos (MP4, WEBM, MOV, etc.)
- ✅ Documents (PDF, DOC, etc.)
- ✅ Archives (ZIP, RAR, 7Z, etc.)

You can customize this in the Download Options section.

---

## Understanding the Interface

### Main Window Layout

```
┌─────────────────────────────────────────────────────┐
│  [Menu Bar]                                         │
├─────────────────────────────────────────────────────┤
│  URL Input                                          │
│  [Paste URLs here - one per line for batch]        │
│                                                     │
│  [Select Folder]  /path/to/downloads                │
├─────────────────────────────────────────────────────┤
│  Download Options:                                  │
│  ☑ Images  ☑ Videos  ☑ Documents  ☑ Archives       │
├─────────────────────────────────────────────────────┤
│  [Download] [Cancel]                                │
├─────────────────────────────────────────────────────┤
│  Progress Bar: [████████░░] 78%                     │
├─────────────────────────────────────────────────────┤
│  Log Messages:                                      │
│  12:34:56 - Starting download...                    │
│  12:34:57 - Found 45 files                          │
│  12:34:58 - Downloading: image001.jpg               │
└─────────────────────────────────────────────────────┘
```

### URL Input

- **Single URL**: Paste one URL to download from that page/profile
- **Batch URLs**: Paste multiple URLs (one per line) to download from many sources
- **Drag & Drop**: Drop a text file containing URLs to import them all

### Download Options

Toggle what file types to download:

- **Images**: JPG, PNG, GIF, BMP, TIFF, WEBP
- **Videos**: MP4, MKV, WEBM, MOV, AVI, FLV
- **Documents**: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX
- **Archives**: ZIP, RAR, 7Z, TAR, GZ

**Tip**: Uncheck file types you don't want to save bandwidth and time.

### Log Panel

The log shows real-time information:

- **INFO**: Normal operation messages
- **WARNING**: Non-critical issues (e.g., file already exists)
- **ERROR**: Problems that need attention

You can:
- Scroll to view history
- Right-click to copy messages
- Click "Clear" to reset the log

---

## Your First Download

Let's walk through a complete download:

### Step 1: Copy a URL

Find a page you want to download from. Examples:

- A creator profile: `https://coomer.su/onlyfans/user/username`
- A single post: `https://kemono.su/patreon/user/12345/post/67890`
- An album: `https://erome.com/a/AbCdEf`
- A YouTube video: `https://youtube.com/watch?v=...`

Copy the URL to your clipboard (Ctrl+C or Cmd+C).

### Step 2: Paste the URL

1. Click in the URL input area
2. Paste the URL (Ctrl+V or Cmd+V)
3. The URL should appear in the text box

**For Batch Downloads**:
- Paste multiple URLs, one per line
- Empty lines are automatically ignored
- Invalid URLs are highlighted

### Step 3: Select Download Folder

1. Click **"Select Folder"**
2. Navigate to where you want files saved
3. Click "Select Folder" or "OK"

The folder path will appear below the button. You can click it later to open the folder in your file explorer.

### Step 4: Choose File Types (Optional)

The checkboxes determine what to download:

- Leave all checked to download everything
- Uncheck boxes to skip certain file types

For example, to download only images:
- ☑ Images
- ☐ Videos
- ☐ Documents
- ☐ Archives

### Step 5: Start Download

1. Click the **"Download"** button
2. The progress bar will show overall progress
3. The log will show detailed status
4. Download speed and ETA appear at the bottom

**During Download**:
- Progress bar fills as files complete
- Current file being downloaded is shown
- Speed (MB/s) and estimated time remaining (ETA) update live

### Step 6: Wait for Completion

The download will:
1. Fetch the page/profile information
2. Find all media files matching your options
3. Download each file
4. Skip files you've already downloaded (duplicates)
5. Show completion message

**Tip**: You can minimize CoomerDL and it will continue downloading in the background.

### Step 7: Access Your Files

When complete:

1. Click the folder path to open the download location
2. Or navigate to your selected folder manually

Files are organized by default as:
```
DownloadFolder/
  ├── site-name/
  │   ├── username/
  │   │   ├── post-id/
  │   │   │   ├── image1.jpg
  │   │   │   ├── image2.jpg
  │   │   │   └── video1.mp4
```

You can change this structure in Settings → Structure.

---

## Troubleshooting Your First Download

### "No files found"

**Possible causes**:
- The URL might not contain downloadable media
- The page might require authentication (login)
- The site might not be supported

**Solutions**:
- Check that the URL works in your browser
- For private content, see the Cookies guide (Settings → Cookies)
- Try a different URL from a supported site

### "Download failed" or "Connection error"

**Possible causes**:
- No internet connection
- Site is temporarily down
- Rate limiting (too many requests)

**Solutions**:
- Check your internet connection
- Wait a few minutes and try again
- Reduce download threads in Settings (Settings → Downloads → Max Downloads)

### Files are incomplete or corrupted

**Possible causes**:
- Download was interrupted
- Connection issues during download

**Solutions**:
- Delete incomplete files
- Try downloading again (CoomerDL will resume where it left off)
- Check your internet connection stability

### Application is slow or unresponsive

**Possible causes**:
- Too many simultaneous downloads
- Large files being processed
- Low system resources

**Solutions**:
- Reduce max downloads in Settings (recommended: 3-5)
- Close other applications to free up memory
- Wait for current operations to complete

---

## Next Steps

Now that you've completed your first download, explore more features:

### Learn More Features

- **[Features Guide](FEATURES.md)** - Detailed guide to all features
- **[FAQ](FAQ.md)** - Common questions and answers
- **[Troubleshooting](TROUBLESHOOTING.md)** - Solve common problems

### Configure Advanced Settings

- **Proxy Support**: Use a proxy for downloads
- **Bandwidth Limiting**: Control download speed
- **File Filters**: Filter by size, date, or type
- **Custom Naming**: Customize how files are named
- **Cookie Import**: Access private/premium content

### Get Help

If you encounter issues:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Read the [FAQ](FAQ.md)
3. Search [GitHub Issues](https://github.com/primoscope/CoomerDL/issues)
4. Open a new issue if your problem isn't covered

### Stay Updated

- Watch the GitHub repository for new releases
- Check the [Changelog](../../README.md#changelog) for new features
- Join the community discussions

---

## Tips for Success

### ✅ Do's

- **Start Small**: Try a single post before downloading an entire profile
- **Check Space**: Ensure you have enough disk space
- **Be Patient**: Large profiles can take hours to download
- **Use Batch Mode**: Paste multiple URLs for efficient bulk downloads
- **Update Regularly**: Keep CoomerDL up to date for best compatibility

### ❌ Don'ts

- **Don't Use Max Threads**: 10 simultaneous downloads can overwhelm servers
- **Don't Download Repeatedly**: Files are tracked; re-downloading is unnecessary
- **Don't Ignore Errors**: Check logs if something fails
- **Don't Forget Backups**: Keep important downloads backed up
- **Don't Share Cookies**: Keep your authentication cookies private

---

## Quick Reference Card

| Action | How To |
|--------|--------|
| Paste URL | Click URL box, Ctrl+V (Cmd+V on Mac) |
| Batch URLs | Paste multiple URLs, one per line |
| Select Folder | Click "Select Folder" button |
| Start Download | Click "Download" button |
| Cancel Download | Click "Cancel" button |
| Open Settings | Menu → Settings |
| View History | Menu → History |
| Change Language | Settings → General → Language |
| Change Theme | Settings → General → Theme |
| Open Download Folder | Click the folder path text |

---

**Happy Downloading!** 🎉

For more advanced usage, see the [Features Guide](FEATURES.md).
