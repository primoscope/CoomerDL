## 2024-05-23 - Unbounded Log State
**Learning:** The `LogPanel` component accumulated logs indefinitely in React state (`setLogs(prev => [...prev, newLog])`), which would eventually crash the browser tab on long-running sessions.
**Action:** Always implement a sliding window (e.g., `.slice(-1000)`) for log/event streams in the frontend.
