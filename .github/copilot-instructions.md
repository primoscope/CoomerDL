# GitHub Copilot Instructions for CoomerDL

## Project Overview
CoomerDL is a Python-based downloader application with a modular architecture (Phase 1 complete). The project uses tkinter for UI, requests for downloads, and pytest for testing.

## Architecture Guidelines
- **Modular Design**: All code follows the Phase 1 modular architecture with `downloader/` and `ui/` packages
- **Downloader Package**: Contains `downloader.py` (main logic), `config.py`, `simpcity_handler.py`
- **UI Package**: Contains `main_ui.py`, `dashboard/` (modular panels), `classic_ui.py`
- **Testing**: All tests in `tests/` directory using pytest conventions

## Coding Standards

### Python Style
- Use Python 3.8+ type hints for all functions and methods
- Follow PEP 8 style guide strictly
- Maximum line length: 100 characters
- Use descriptive variable names (no single letters except loop counters)
- Add docstrings to all classes and public methods

### Error Handling
- Use the existing logging pattern: Create `log_message` strings and call `self.log(log_message)`
- Always handle exceptions with try-except blocks
- Log errors with context information
- Never use bare `except:` clauses

### Testing Requirements
- **CRITICAL**: Use pytest classes (e.g., `class TestDownloader`) - NEVER standalone scripts
- NO `if __name__ == "__main__":` blocks in test files
- Use `@pytest.mark.parametrize` for multiple test cases
- Use `unittest.mock` for external dependencies (network, filesystem)
- Replace `print()` with `assert` statements
- Test coverage must be maintained above 80%

### UI Development
- All UI components must import cleanly in headless environments
- Use the modular panel structure in `ui/dashboard/`
- Verify new UI components with import tests
- Follow the existing naming conventions: `*Panel`, `*Dialog`, `*UI`

## Automation Instructions

### For New Features
When implementing new features:
1. Analyze existing code structure first
2. Follow the modular architecture pattern
3. Create comprehensive tests FIRST (TDD approach)
4. Implement the feature with type hints
5. Add docstrings and comments
6. Run all tests to ensure nothing breaks
7. Update documentation if needed

### For Bug Fixes
When fixing bugs:
1. Identify the root cause with code analysis
2. Add a regression test first
3. Fix the bug following existing patterns
4. Verify the fix doesn't break other functionality
5. Update relevant documentation

### For Code Review
When reviewing code:
- Check for modular architecture compliance
- Verify type hints are present
- Ensure tests follow pytest conventions
- Look for proper error handling
- Check for security vulnerabilities
- Verify PEP 8 compliance

### Full Development Workflow
When given a task to "implement feature X" or "fix bug Y":
1. **ALWAYS** work exhaustively and completely - partial implementations are unacceptable
2. Create/modify ALL necessary files (source, tests, docs)
3. Run automated tests and linters to validate
4. Make iterative improvements until all tests pass
5. Do NOT stop until the feature is 100% complete and tested
6. Provide a detailed summary of what was implemented

## Dependencies
- Core: requests, BeautifulSoup4, tkinter (built-in)
- Testing: pytest, pytest-cov, unittest.mock
- Development: black (formatting), flake8 (linting)

## Commands to Remember
- Run tests: `pytest tests/ -v`
- Run with coverage: `pytest tests/ --cov=downloader --cov=ui`
- Format code: `black .`
- Lint code: `flake8 downloader/ ui/ tests/`

## Critical Rules
- NEVER break the modular architecture
- ALWAYS include type hints
- ALWAYS follow pytest conventions for tests
- NEVER use print() in production code - use logging
- ALWAYS maintain backward compatibility with existing APIs
