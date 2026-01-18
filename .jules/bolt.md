## 2025-02-15 - Unbounded Log State Growth
**Learning:** The `LogPanel` component was appending logs indefinitely to React state without a ceiling, causing a memory leak and progressive rendering slowdown. This is a critical pattern to watch in any WebSocket-driven real-time component.
**Action:** Always implement a sliding window (e.g., `.slice(-MAX)`) for high-frequency real-time data streams in the frontend.
