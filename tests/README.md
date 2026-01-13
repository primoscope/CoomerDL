# CoomerDL Unit Tests

This directory contains unit tests for the CoomerDL application's core logic components.

## Test Structure

- **`conftest.py`**: Shared pytest fixtures and configuration
- **`test_base_downloader.py`**: Tests for `downloader/base.py` (BaseDownloader class)
- **`test_factory.py`**: Tests for `downloader/factory.py` (DownloaderFactory class)
- **`test_download_queue.py`**: Tests for `app/models/download_queue.py` (DownloadQueue class)

## Running Tests

### Run all tests
```bash
pytest
```

### Run with verbose output
```bash
pytest -v
```

### Run specific test file
```bash
pytest tests/test_base_downloader.py -v
```

### Run specific test class
```bash
pytest tests/test_base_downloader.py::TestBaseDownloaderCancellation -v
```

### Run specific test
```bash
pytest tests/test_base_downloader.py::TestBaseDownloaderCancellation::test_request_cancel -v
```

## Test Coverage

Current test coverage includes:

### BaseDownloader (24 tests)
- Initialization with various configurations
- Cancellation mechanism
- Filename sanitization
- File type detection
- Progress reporting callbacks

### DownloaderFactory (13 tests)
- Downloader registration
- URL-based downloader selection
- Supported sites enumeration

### DownloadQueue (33 tests)
- Add/remove operations
- Priority ordering
- Status updates
- Persistence (with mocked I/O)
- Queue utilities

## Key Testing Principles

1. **No Real Network Calls**: All HTTP requests are mocked
2. **No Real File I/O**: File operations use `tmp_path` or are mocked
3. **Isolation**: Tests use fixtures to ensure clean state
4. **No Application Code Changes**: Tests are designed to work with existing code

## Fixtures

### `download_folder`
Provides a temporary directory for download tests using pytest's `tmp_path`.

### `download_options`
Provides a default `DownloadOptions` instance with standard settings.

### `mock_queue_file`
Mocks the queue persistence file path to use `tmp_path`.

### `queue`
Provides a fresh `DownloadQueue` instance for each test.

## Adding New Tests

1. Create test file: `tests/test_<module_name>.py`
2. Import necessary modules and fixtures
3. Organize tests into classes by functionality
4. Use descriptive test names: `test_<what_is_being_tested>`
5. Mock external dependencies (network, file I/O, etc.)
6. Use assertions to verify expected behavior

Example:
```python
def test_my_new_feature(download_folder):
    """Test that my new feature works correctly."""
    # Setup
    downloader = MockDownloader(download_folder=download_folder)
    
    # Execute
    result = downloader.some_method()
    
    # Assert
    assert result.success is True
```
