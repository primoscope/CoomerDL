---
paths:
  - "ui/**/*.py"
---

# UI Development Instructions

When working on UI files:

## Architecture
- Classic UI: Single-window interface (`classic_ui.py`)
- Dashboard UI: Multi-tab interface with modular panels
- All panels inherit from or follow existing patterns

## Component Structure
```python
class MyPanel:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self):
        # Build UI components
        pass
```

## UI Guidelines
- Use ttk widgets for modern appearance
- Follow existing layout patterns
- Ensure components work in headless environments
- Add proper event handlers with error handling
- Use threading for long-running operations

## Testing UI Components
- Create import verification tests
- Test that classes/methods exist
- Mock tkinter components for unit tests
- Skip full UI tests in headless environments
