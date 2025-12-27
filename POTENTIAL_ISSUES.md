# Potential Issues and Blockers

> **Purpose**: Document known issues, edge cases, and potential blockers that might affect task implementation. AI coding agents should check this file before starting work.

---

## Quick Reference

| Issue | Affects Tasks | Severity | Status |
|-------|---------------|----------|--------|
| [Rate limiting](#issue-001-rate-limiting) | All downloaders | Medium | Known |
| [Cloudflare protection](#issue-002-cloudflare-protection) | SimpCity, some Bunkr | High | Workaround exists |
| [CTk widget limitations](#issue-003-customtkinter-limitations) | UI tasks | Medium | Known |
| [Thread safety in UI](#issue-004-thread-safety-in-ui-updates) | All UI tasks | High | Pattern exists |
| [Database locking](#issue-005-sqlite-database-locking) | Database tasks | Medium | Known |
| [Translation system](#issue-006-translation-system-complexity) | All UI tasks | Low | Known |

---

## Issue Details

### ISSUE-001: Rate Limiting

**Affects**: All downloader tasks

**Problem**: 
Websites implement rate limiting that may cause 429 errors during testing.
- Coomer/Kemono: ~1 request/second safe
- Bunkr: Aggressive rate limiting
- Erome: Moderate rate limiting

**Impact on Development**:
- Testing may fail due to temporary bans
- Hard to reproduce issues consistently
- May need to wait between test runs

**Workaround**:
```python
# Add delays between requests during testing
import time
time.sleep(2)  # Between page requests
```

**Agent Instructions**:
- Don't assume 429 errors are bugs in your code
- Add appropriate delays in new code
- Test with small batches first

---

### ISSUE-002: Cloudflare Protection

**Affects**: FEATURE tasks for SimpCity, some Bunkr URLs

**Problem**:
Some sites use Cloudflare protection that blocks automated requests.
- SimpCity uses cloudscraper (already implemented)
- Some Bunkr mirrors have Cloudflare
- Protection can change without notice

**Impact on Development**:
- Standard requests may fail with 403
- cloudscraper may need updates
- Tests may be flaky

**Current Implementation**:
```python
# In simpcity.py
import cloudscraper
scraper = cloudscraper.create_scraper()
```

**Agent Instructions**:
- Don't remove cloudscraper dependency
- Test with real URLs, not mocks, for Cloudflare-protected sites
- If requests fail with 403/503, it's likely Cloudflare, not a bug

---

### ISSUE-003: CustomTkinter Limitations

**Affects**: All UI tasks (FEATURE-001, FEATURE-003, ARCH-001)

**Problem**:
CustomTkinter has limitations compared to standard tkinter:
- No native drag-and-drop support
- Limited widget customization
- Some widgets behave differently than tkinter equivalents
- CTkTextbox has different API than tkinter Text

**Known CTk Issues**:
```python
# CTkTextbox get() is different from tkinter
# tkinter: text.get("1.0", "end")
# CTk: textbox.get("1.0", "end-1c")  # Note: end-1c to avoid extra newline

# CTkOptionMenu has no get() method by default
# Use variable: ctk.StringVar()
```

**Agent Instructions**:
- Always use `"end-1c"` not `"end"` with CTkTextbox
- Test UI changes manually - automated UI testing is limited
- Check CTk documentation for widget-specific APIs

---

### ISSUE-004: Thread Safety in UI Updates

**Affects**: All tasks that update UI from download threads

**Problem**:
Tkinter/CTk is not thread-safe. UI updates from background threads cause crashes.

**Current Pattern (MUST FOLLOW)**:
```python
# In ui.py - the safe way to update UI from threads
def add_log_message_safe(self, message):
    """Thread-safe method to add log messages."""
    self.log_queue.put(message)
    self.after(0, self._process_log_queue)

def _process_log_queue(self):
    """Process queued log messages on main thread."""
    while not self.log_queue.empty():
        message = self.log_queue.get()
        self._add_log_message(message)
```

**Agent Instructions**:
- NEVER call widget methods directly from download threads
- ALWAYS use `self.after()` or queue pattern for thread→UI communication
- Test cancellation - it's a common source of thread issues

---

### ISSUE-005: SQLite Database Locking

**Affects**: BUG tasks, Database-related features

**Problem**:
SQLite has limited concurrent access:
- Only one writer at a time
- Readers can block writers
- Long transactions cause "database is locked" errors

**Current Implementation Issues**:
```python
# In downloader.py - connection kept open
self.conn = sqlite3.connect(db_path)
# This can cause locking issues with concurrent downloads
```

**Potential Fixes**:
```python
# Option 1: Use WAL mode (already done)
conn.execute("PRAGMA journal_mode=WAL")

# Option 2: Short-lived connections
def insert_download(self, ...):
    with sqlite3.connect(self.db_path) as conn:
        conn.execute(...)

# Option 3: Connection pooling (more complex)
```

**Agent Instructions**:
- Don't hold database connections open longer than needed
- Use `with` statement for automatic cleanup
- Test with multiple concurrent downloads

---

### ISSUE-006: Translation System Complexity

**Affects**: All UI tasks

**Problem**:
The translation system has some quirks:
- Translation files are JSON in resources/locales/
- Not all strings are translated
- Some downloaders have their own `tr()` method
- Mixed languages in comments (Spanish/English)

**How It Works**:
```python
# In ui.py
self.translations = load_translations(language)

# Usage
self.tr("download_complete")  # Looks up in translations dict

# With formatting
self.tr("files_found", count=45)  # "Found {count} files"
```

**Agent Instructions**:
- Use `self.tr("key")` for all user-visible strings
- Add new translation keys to ALL language files
- Test with at least English (en) to verify strings display
- Don't fix Spanish comments unless specifically asked

---

## Task-Specific Issues

### For FEATURE-001 (Batch URL Input)

**Might Not Work**:
1. **Drag-and-drop**: CTk doesn't support native DnD. Would need `tkinterdnd2` package.
   - Recommendation: Skip drag-and-drop, focus on paste functionality
   
2. **URL validation performance**: Validating many URLs synchronously may freeze UI
   - Recommendation: Validate in background thread, show spinner

3. **Progress tracking**: Current progress system assumes single URL
   - Recommendation: Add batch progress counter, keep individual progress

---

### For FEATURE-002 (BaseDownloader)

**Might Not Work**:
1. **Different authentication methods**: SimpCity uses cookies, others don't
   - Recommendation: Add optional `cookies` parameter to base class

2. **Different URL patterns**: Each site has unique URL structure
   - Recommendation: `supports_url()` is abstract - each class implements own logic

3. **Progress callback signatures**: Slightly different across downloaders
   - Recommendation: Standardize to `(downloaded_bytes, total_bytes, metadata_dict)`

---

### For FEATURE-003 (Download Queue)

**Might Not Work**:
1. **Persistence**: If app crashes, queue JSON may be corrupted
   - Recommendation: Use atomic writes (write to temp, then rename)

2. **Queue ordering**: Priority changes during download may cause issues
   - Recommendation: Lock queue during active download, apply changes after

3. **Memory usage**: Large queues may consume memory
   - Recommendation: Limit queue size or implement lazy loading

---

### For ARCH-001 (Split ui.py)

**Might Not Work**:
1. **Circular imports**: Split modules may import each other
   - Recommendation: Use dependency injection, pass callbacks not imports

2. **Shared state**: Many UI components access `self.settings`, `self.translations`
   - Recommendation: Create shared context object passed to all panels

3. **Event handling**: Current code has tightly coupled event handlers
   - Recommendation: Use event bus pattern or explicit callback registration

---

## Testing Limitations

### What CAN Be Tested
- URL parsing and validation (unit tests)
- File naming logic (unit tests)
- Configuration loading/saving (unit tests)
- Data class serialization (unit tests)

### What CANNOT Be Easily Tested
- Actual downloads (requires network, rate limits)
- UI interactions (requires manual testing or complex setup)
- Cloudflare-protected sites (requires real browser context)
- Database in multi-threaded scenarios (timing-dependent)

### Recommended Test Approach
```python
# Use mocking for network requests
from unittest.mock import patch, MagicMock

@patch('requests.Session.get')
def test_download_logic(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = b'fake image data'
    # Test download logic without network
```

---

## Environment-Specific Issues

### Windows
- Long file paths may fail (>260 chars)
- Some Unicode filenames may cause issues
- Console encoding may affect logging

### macOS
- CustomTkinter may look different
- File system is case-insensitive

### Linux
- Missing system dependencies for tkinter
- Need `python3-tk` package installed

---

## When to Report New Issues

Add to this file if you encounter:
1. Consistent failures not related to your code changes
2. Platform-specific behavior differences
3. Third-party API changes (website structure changes)
4. New Cloudflare or anti-bot measures
5. Performance issues at scale

**Format for new issues**:
```markdown
### ISSUE-XXX: Title

**Affects**: Task IDs

**Problem**: Description

**Impact on Development**: How it affects coding

**Workaround**: If any exists

**Agent Instructions**: What to do/not do
```

---

*Last updated: December 2024*
