# Test Suite Documentation

This directory contains automated tests for the CoomerDL application.

## Overview

The test suite provides comprehensive coverage of core utilities without modifying the application code. Tests are organized into four main categories:

1. **URL Parsing Tests** (`test_utils.py`) - 11 tests
2. **Downloader Utilities Tests** (`test_downloader.py`) - 15 tests  
3. **URL Routing Tests** (`test_url_routing.py`) - 9 tests
4. **Settings Persistence Tests** (`test_settings.py`) - 5 tests

**Total: 40 tests**

## Running Tests

### Prerequisites

Install pytest if not already installed:
```bash
pip install pytest
```

### Run All Tests

```bash
# From the repository root
python -m pytest tests/

# With verbose output
python -m pytest tests/ -v

# With coverage report (if pytest-cov is installed)
python -m pytest tests/ --cov=app --cov=downloader
```

### Run Specific Test Files

```bash
# Test URL parsing functions
python -m pytest tests/test_utils.py -v

# Test downloader utilities
python -m pytest tests/test_downloader.py -v

# Test URL routing logic
python -m pytest tests/test_url_routing.py -v

# Test settings persistence
python -m pytest tests/test_settings.py -v
```

### Run Specific Test Classes or Methods

```bash
# Run a specific test class
python -m pytest tests/test_downloader.py::TestSanitizeFilename -v

# Run a specific test method
python -m pytest tests/test_utils.py::TestExtractCkParameters::test_full_url_with_post -v
```

## Test Structure

### Fixtures (`conftest.py`)

- **`mock_settings`**: Provides a standard configuration dictionary for testing
- **`temp_download_dir`**: Creates a temporary directory for download testing using pytest's `tmp_path` fixture

### Test Files

#### `test_utils.py` - URL Parsing Functions
Tests the URL parsing utilities from `app.ui`:
- `extract_ck_parameters(url)` - Extracts service, user, and post from URLs
- `extract_ck_query(url)` - Extracts query parameters and offsets

#### `test_downloader.py` - Filename Utilities
Tests the core filename handling from `downloader.downloader`:
- `Downloader.sanitize_filename()` - Validates removal of invalid characters
- `Downloader.get_filename()` - Tests all 4 naming modes (0-3) with various inputs

#### `test_url_routing.py` - URL Routing Logic
Tests the URL-to-downloader mapping logic:
- Erome URL detection (album vs profile)
- Bunkr URL detection with various TLDs
- Coomer/Kemono URL detection
- SimpCity URL detection
- Jpg5 URL detection
- Routing priority and invalid URL handling

#### `test_settings.py` - Configuration Persistence
Tests settings loading and saving from `app.settings_window`:
- Default settings loading
- Save and load roundtrip
- Directory creation
- Corrupted JSON handling
- Data type preservation

## Design Decisions

### GUI Mocking
Since the application uses tkinter/customtkinter for the GUI, tests mock these modules to avoid GUI dependencies. This allows tests to run in headless environments (CI/CD pipelines, Docker containers, etc.).

### No Source Code Modifications
All tests are created in the `tests/` directory without modifying any application code in `app/` or `downloader/`. This ensures:
- No conflicts with ongoing UI development
- Clean separation of test code from production code
- Easy maintenance and updates

### Focus on Pure Logic
Tests target pure logic functions that don't require GUI interaction:
- URL parsing and validation
- Filename sanitization and generation
- Configuration persistence
- URL pattern matching

## Maintenance

### Adding New Tests

1. Create test files following the naming convention `test_*.py`
2. Organize tests into classes using `Test*` prefix
3. Use descriptive test method names with `test_*` prefix
4. Add docstrings explaining what each test validates
5. Use fixtures from `conftest.py` where appropriate

### Test Conventions

- Each test should be independent and not rely on other tests
- Use assertions to validate expected behavior
- Clean up resources using pytest fixtures or teardown methods
- Mock external dependencies (network, filesystem) when appropriate

## Continuous Integration

These tests are designed to run in CI/CD environments. They:
- Don't require GUI display
- Use temporary directories for file operations
- Mock external dependencies
- Run quickly (< 1 second for the full suite)

## Troubleshooting

### Import Errors
If you encounter import errors, ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### GUI Module Errors
Tests already mock tkinter/customtkinter. If you see GUI-related errors, verify the mock setup in test files is correct.

### Test Failures
If tests fail after code changes:
1. Review the test output to understand which assertions failed
2. Verify the behavior change is intentional
3. Update test expectations if the new behavior is correct
4. Add new tests for new features or edge cases

## Coverage

Current test coverage focuses on:
- ✅ URL parsing and query extraction
- ✅ Filename sanitization and generation (all modes)
- ✅ URL routing logic for all supported sites
- ✅ Settings persistence and error handling

Areas not currently covered (intentionally):
- ❌ GUI components (tkinter/customtkinter widgets)
- ❌ Network requests (downloaders' HTTP operations)
- ❌ Database operations (download history)
- ❌ Thread/process management

These areas were excluded per project requirements to avoid conflicts with active development and focus on stable core utilities.
