---
paths:
  - "tests/**/*.py"
---

# Testing Instructions

When working on test files:

## Structure
- Use pytest test classes: `class TestClassName:`
- Group related tests in the same class
- Use `@pytest.fixture` for reusable setup
- Use `@pytest.mark.parametrize` for multiple cases

## Naming
- Test files: `test_<module_name>.py`
- Test classes: `TestClassName`
- Test methods: `test_<functionality>_<scenario>`

## Patterns to AVOID
```python
# ❌ BAD - No standalone scripts
if __name__ == "__main__":
    main()

# ❌ BAD - No print statements
print("Test passed")

# ❌ BAD - No boolean returns
return True
```

## Patterns to USE
```python
# ✅ GOOD - Pytest class structure
class TestDownloader:
    @pytest.fixture
    def downloader(self):
        return Downloader()
    
    def test_download_success(self, downloader):
        result = downloader.download("url")
        assert result.status == 200
```

## Mock Requirements
- Mock ALL external network calls
- Mock ALL file system operations
- Use `unittest.mock.patch` decorator
- Check for `_mock_name` attribute to detect mocks
