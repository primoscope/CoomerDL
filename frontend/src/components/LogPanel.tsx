import React, { useEffect, useState, useRef, useMemo } from 'react'
import { Terminal, Trash2 } from 'lucide-react'
import { logsWS } from '@/services/websocket'
import type { LogMessage } from '@/types/api'

// Helper for log colors
const getLogColor = (level: string): string => {
  switch (level.toUpperCase()) {
    case 'ERROR': return '#f44336'
    case 'WARNING': return '#ff9800'
    case 'INFO': return '#2196F3'
    case 'SUCCESS': return '#4caf50'
    default: return '#999'
  }
}

// Memoized LogItem component to prevent unnecessary re-renders
const LogItem = React.memo(({ log }: { log: LogMessage }) => (
  <div style={{ marginBottom: '4px' }}>
    <span style={{ color: '#666' }}>
      {new Date(log.timestamp).toLocaleTimeString()}
    </span>
    {' '}
    <span style={{
      color: getLogColor(log.level),
      fontWeight: 'bold',
      marginRight: '8px'
    }}>
      [{log.level.toUpperCase()}]
    </span>
    <span style={{ color: '#e0e0e0' }}>
      {log.message}
    </span>
  </div>
))

LogItem.displayName = 'LogItem'

const LogPanel: React.FC = () => {
  const [logs, setLogs] = useState<LogMessage[]>([])
  const [autoScroll, setAutoScroll] = useState(true)
  const [filter, setFilter] = useState<string>('all')
  const logContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Listen for log messages via WebSocket
    const handleLogMessage = (data: any) => {
      if (data.type === 'log') {
        const logMessage: LogMessage = {
          timestamp: data.timestamp,
          level: data.level,
          message: data.message,
        }
        // Limit logs to last 1000 items to prevent memory issues
        setLogs(prev => {
          const newLogs = [...prev, logMessage]
          if (newLogs.length > 1000) {
            return newLogs.slice(-1000)
          }
          return newLogs
        })
      }
    }

    logsWS.on('log', handleLogMessage)

    return () => {
      logsWS.off('log', handleLogMessage)
    }
  }, [])

  useEffect(() => {
    // Auto-scroll to bottom when new logs arrive
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [logs, autoScroll])

  const clearLogs = () => {
    setLogs([])
  }

  // Memoize filtered logs to prevent recalculation on every render
  const filteredLogs = useMemo(() => {
    return filter === 'all'
      ? logs
      : logs.filter(log => log.level.toLowerCase() === filter.toLowerCase())
  }, [logs, filter])

  return (
    <div className="card">
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '16px',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <h2 style={{ fontSize: '20px', margin: 0 }}>
          <Terminal size={20} style={{ verticalAlign: 'middle', marginRight: '8px' }} />
          Logs ({filteredLogs.length})
        </h2>
        
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
          <select
            className="input"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            style={{ width: 'auto', padding: '8px 12px' }}
          >
            <option value="all">All Logs</option>
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
          </select>

          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              className="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
            />
            <span style={{ fontSize: '14px' }}>Auto-scroll</span>
          </label>

          <button
            className="button button-secondary"
            onClick={clearLogs}
            style={{ padding: '8px 12px', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <Trash2 size={16} />
            Clear
          </button>
        </div>
      </div>

      <div
        ref={logContainerRef}
        style={{
          background: '#000',
          border: '1px solid var(--border-color)',
          borderRadius: '6px',
          padding: '12px',
          maxHeight: '400px',
          overflowY: 'auto',
          fontFamily: 'monospace',
          fontSize: '13px',
          lineHeight: '1.6',
        }}
      >
        {filteredLogs.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
            No logs to display
          </div>
        ) : (
          filteredLogs.map((log, index) => (
            // Using timestamp as part of key for better stability if possible,
            // but relying on index is risky if logs are filtered.
            // Ideally logs should have unique IDs.
            // For now, since it's an append-only list (mostly), index is acceptable but fragile.
            // Let's try to make a unique key if possible. LogMessage doesn't have ID.
            // Using index + timestamp combination.
            <LogItem key={`${index}-${log.timestamp}`} log={log} />
          ))
        )}
      </div>
    </div>
  )
}

export default LogPanel
