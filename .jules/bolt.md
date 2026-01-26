## 2026-01-26 - Frontend List Performance Anti-Pattern
**Learning:** Using array index as `key` in a FIFO list (like logs) causes every item to re-render when the list is shifted/truncated, negating React's reconciliation benefits.
**Action:** Always generate stable unique IDs for append-only streams that get truncated, and memoize the list item component.
