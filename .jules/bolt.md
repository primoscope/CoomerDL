## 2024-05-23 - Frontend Log State Management
**Learning:** The `LogPanel` component was appending logs indefinitely to the React state (`[...prev, new]`) without any limit. In a long-running WebSocket application, this inevitably leads to memory leaks and severe UI lag as the DOM grows unbounded.
**Action:** Always implement a fixed-size buffer (sliding window) for real-time log or event streams in the frontend. Use `slice(-MAX_ITEMS)` during state updates and ensure list items have stable IDs for efficient reconciliation.
