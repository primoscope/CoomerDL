import React, { useEffect, useState, useRef, useMemo } from 'react'
import { Terminal, Trash2 } from 'lucide-react'
import { logsWS } from '@/services/websocket'
import type { LogMessage } from '@/types/api'

// Extend LogMessage to include a unique ID for rendering performance
interface LogItemData extends LogMessage {
  id: string
}

const MAX_LOGS = 1000

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
const LogItem = React.memo(({ log, color }: { log: LogItemData, color: string }) => (
  <div style={{ marginBottom: '4px' }}>
    <span style={{ color: '#666' }}>
      {new Date(log.timestamp).toLocaleTimeString()}
    </span>
    {' '}
    <span style={{
      color: color,
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
  const [logs, setLogs] = useState<LogItemData[]>([])
  const [autoScroll, setAutoScroll] = useState(true)
  const [filter, setFilter] = useState<string>('all')
  const logContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Listen for log messages via WebSocket
    const handleLogMessage = (data: any) => {
      if (data.type === 'log') {
        const logMessage: LogItemData = {
          // Generate a unique ID to ensure stable keys and avoid re-renders of existing items
          id: Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
          timestamp: data.timestamp,
          level: data.level,
          message: data.message,
        }

        setLogs(prev => {
          // Append new log and keep only the last MAX_LOGS
          const newLogs = [...prev, logMessage]
          if (newLogs.length > MAX_LOGS) {
            return newLogs.slice(newLogs.length - MAX_LOGS)
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

  const filteredLogs = useMemo(() =>
    filter === 'all'
      ? logs
      : logs.filter(log => log.level.toLowerCase() === filter.toLowerCase()),
    [logs, filter]
  )

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
          filteredLogs.map((log) => (
            <LogItem
              key={log.id}
              log={log}
              color={getLogColor(log.level)}
            />
          ))
        )}
      </div>
    </div>
  )
}

export default LogPanel
