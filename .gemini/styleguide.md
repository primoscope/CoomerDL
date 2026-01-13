# CoomerDL Coding Style Guide

## General Principles
- **Modularity**: Always follow the Phase 1 modular architecture. Use the `downloader` and `ui` packages correctly.
- **Type Hinting**: All new functions and methods must include Python type hints.
- **Error Handling**: Use the existing `log_message` and `self.log()` patterns in the downloader.

## Testing Standards
- **Pytest**: Use `pytest` classes and fixtures. Do not use standalone scripts or `if __name__ == "__main__":` blocks.
- **Mocking**: Use `unittest.mock` for external network calls.
- **In-process Verification**: New UI components must have verification tests to ensure proper imports and structure.

## Review Output Format
1. Summary of changes (3-5 bullets).
2. Critical/High issues as inline comments.
3. Medium/Low suggestions for optimization.
4. Test coverage check: Always call out missing tests for new logic.
