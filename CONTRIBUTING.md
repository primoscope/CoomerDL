# Contributing to CoomerDL

Thank you for your interest in contributing to CoomerDL! This guide will help you get started.

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Code Style and Standards](#code-style-and-standards)
4. [Testing Guidelines](#testing-guidelines)
5. [Gemini Code Assist Enterprise Setup](#gemini-code-assist-enterprise-setup)
6. [Pull Request Process](#pull-request-process)

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of Python and CustomTkinter (for UI work)

### Quick Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/CoomerDL.git`
3. Install dependencies: `pip install -r requirements.txt`
4. Run tests: `pytest tests/`
5. Start the app: `python main.py`

---

## Development Setup

### Project Structure

```
CoomerDL/
├── app/                    # UI components
│   ├── window/            # Modular UI panels
│   ├── dialogs/           # Dialog windows
│   └── models/            # UI data models
├── downloader/            # Download engine
│   ├── base.py           # Abstract base class
│   ├── factory.py        # URL routing
│   └── queue.py          # Job queue system
├── tests/                 # Test suite (242+ tests)
├── resources/             # Config, translations, icons
└── .gemini/              # Gemini Code Assist config
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_base_downloader.py

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=downloader --cov=app
```

---

## Code Style and Standards

### General Principles

1. **Modularity**: Follow the Phase 1 modular architecture
   - Separate concerns between `downloader/` and `app/` packages
   - Use dependency injection where possible

2. **Type Hints**: All new functions must include Python type hints
   ```python
   def download(self, url: str, folder: str) -> DownloadResult:
       pass
   ```

3. **Error Handling**: Use consistent logging patterns
   ```python
   self.log(self.tr("Downloading {url}").format(url=url))
   ```

4. **Documentation**: Add docstrings for public APIs
   ```python
   def supports_url(self, url: str) -> bool:
       """Check if this downloader can handle the given URL.
       
       Args:
           url: The URL to check
           
       Returns:
           True if the URL is supported, False otherwise
       """
   ```

### Testing Standards

- **Use pytest**: Write tests using pytest classes and fixtures
- **No standalone scripts**: Avoid `if __name__ == "__main__":` in tests
- **Mock external calls**: Use `unittest.mock` for network requests
- **Test coverage**: Aim for >80% coverage on new code

Example test structure:
```python
class TestMyFeature:
    def test_basic_functionality(self):
        result = my_function("test")
        assert result == expected_value
    
    def test_error_handling(self):
        with pytest.raises(ValueError):
            my_function(None)
```

---

## Gemini Code Assist Enterprise Setup

### For Maintainers

This repository is optimized for **Gemini Code Assist Enterprise**. To enable full AI-powered development:

#### 1. Link Repository to Code Repository Index

In the **Google Cloud Console**:

1. Navigate to **Code Repository Index**
2. Click **Link Repository**
3. Select **GitHub** as the source
4. Authorize and select `rid0-boop/CoomerDL`
5. Wait for initial indexing (may take 10-30 minutes)

#### 2. Enable Enterprise Features

Once indexed, Gemini will have:
- **Codebase-wide context**: Understanding of the entire project structure
- **Pattern recognition**: Suggestions based on existing code patterns
- **Cross-file analysis**: Detection of issues spanning multiple modules
- **Historical context**: Learning from past changes and reviews

#### 3. Using Custom Slash Commands

The `.gemini/commands/` directory provides powerful workflow shortcuts:

- **`/plan`**: Generate implementation plans
  ```
  /plan "add dark mode to settings"
  ```

- **`/test`**: Generate pytest tests
  ```
  /test "downloader/base.py"
  ```

- **`/optimize`**: Audit code for improvements
  ```
  /optimize "app/ui.py lines 100-200"
  ```

### Configuration Files

The `.gemini/` directory contains:

- **`config.yaml`**: Review settings (LOW severity threshold, 80 comment limit)
- **`styleguide.md`**: Project-specific coding standards
- **`commands/*.toml`**: Custom slash command definitions

These ensure Gemini provides:
- Thorough code reviews
- Architecture enforcement
- Test coverage validation
- Consistent suggestions aligned with project patterns

---

## Pull Request Process

### Before Submitting

1. **Run tests**: Ensure all tests pass
   ```bash
   pytest tests/
   ```

2. **Check code style**: Follow PEP 8 and project conventions
   ```bash
   flake8 app/ downloader/
   ```

3. **Update documentation**: If you added features, update relevant docs

4. **Add tests**: New features require new tests

### PR Guidelines

- **Title**: Use clear, descriptive titles
  - Good: "Add resume capability for downloads"
  - Bad: "Fix stuff"

- **Description**: Include:
  - What changed
  - Why it changed
  - How to test it
  - Related issues (if any)

- **Size**: Keep PRs focused and reasonably sized
  - Ideal: <500 lines changed
  - Large PRs are harder to review

- **Commits**: Write clear commit messages
  ```
  Add download resume capability
  
  - Implement partial file tracking with .part extension
  - Add HTTP Range header support for resume
  - Update tests for resume functionality
  ```

### Review Process

1. Automated checks will run (tests, linting)
2. Maintainers will review your code
3. Address any feedback or requested changes
4. Once approved, your PR will be merged

---

## Additional Resources

- **Roadmap**: See [DEVELOPMENT_ROADMAP_V2.md](DEVELOPMENT_ROADMAP_V2.md) for planned features
- **Architecture**: See [PHASE1_IMPLEMENTATION_COMPLETE.md](PHASE1_IMPLEMENTATION_COMPLETE.md)
- **AI Agents**: See README.md section "Contributing with AI Coding Agents"
- **Gemini Docs**: [Gemini Code Assist Documentation](https://developers.google.com/gemini-code-assist/docs)

---

## Questions?

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Discord**: Join our community server (link in README)

We appreciate your contributions! 🎉
