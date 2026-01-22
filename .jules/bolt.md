## 2025-02-12 - Unbounded WebSocket Log Growth
**Learning:** The application receives logs via WebSocket and appends them to a state array indefinitely. In a long-running session, this causes a memory leak and performance degradation as the DOM and React virtual DOM grow without limit.
**Action:** Always implement a buffer limit (e.g., circular buffer or slicing) when accumulating high-frequency real-time data on the frontend.
