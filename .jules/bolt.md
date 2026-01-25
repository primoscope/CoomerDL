## 2024-05-22 - Unbounded State Growth in WebSocket Consumers
**Learning:** The `LogPanel` component allowed the `logs` array to grow indefinitely as new messages arrived via WebSocket. This causes linear memory growth and progressively slower rendering, eventually leading to UI unresponsiveness.
**Action:** Always implement a fixed-size circular buffer or sliding window (e.g., `MAX_LOGS`) for high-frequency data streams to ensure constant memory usage and predictable rendering performance.
