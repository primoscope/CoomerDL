## 2024-05-23 - Unbounded State Growth in React Lists
**Learning:** Found a critical memory leak in `LogPanel` where logs were appended indefinitely (`setLogs(prev => [...prev, newLog])`). In long-running applications (like a downloader), this crashes the browser.
**Action:** Always implement a `MAX_ITEMS` cap (e.g., slice the array) for any state that accumulates real-time events (logs, chat messages, notifications).
