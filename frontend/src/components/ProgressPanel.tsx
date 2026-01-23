import React, { useEffect, useState, memo } from 'react'
import { Activity } from 'lucide-react'
import { downloadsApi } from '@/services/api'
import { progressWS } from '@/services/websocket'
import type { DownloadStatusResponse, ProgressUpdate } from '@/types/api'

// Helper functions moved outside component
const formatSpeed = (bytesPerSecond: number): string => {
  if (bytesPerSecond < 1024) return `${bytesPerSecond.toFixed(0)} B/s`
  if (bytesPerSecond < 1024 * 1024) return `${(bytesPerSecond / 1024).toFixed(1)} KB/s`
  return `${(bytesPerSecond / (1024 * 1024)).toFixed(1)} MB/s`
}

const formatETA = (seconds?: number): string => {
  if (!seconds) return 'Calculating...'
  if (seconds < 60) return `${Math.round(seconds)}s`
  if (seconds < 3600) return `${Math.round(seconds / 60)}m`
  return `${Math.round(seconds / 3600)}h`
}

const getStatusColor = (status: string): string => {
  switch (status) {
    case 'downloading': return '#667eea'
    case 'completed': return '#4caf50'
    case 'failed': return '#f44336'
    case 'cancelled': return '#999'
    default: return '#ff9800'
  }
}

// Memoized item component to prevent unnecessary re-renders
const DownloadItem = memo(({ download }: { download: DownloadStatusResponse }) => (
  <div
    style={{
      padding: '16px',
      background: 'rgba(255,255,255,0.03)',
      borderRadius: '6px',
      border: '1px solid var(--border-color)',
    }}
  >
    <div style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '12px',
      flexWrap: 'wrap',
      gap: '8px'
    }}>
      <div style={{ flex: 1, minWidth: '200px' }}>
        <div style={{
          fontSize: '14px',
          fontWeight: 500,
          marginBottom: '4px',
          wordBreak: 'break-all'
        }}>
          {download.url}
        </div>
        <div style={{ fontSize: '12px', color: '#999' }}>
          {download.current_file || 'Preparing...'}
        </div>
      </div>

      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
        fontSize: '14px'
      }}>
        <span style={{ color: getStatusColor(download.status) }}>
          {download.status.toUpperCase()}
        </span>
        <span>{download.completed_files} / {download.total_files} files</span>
      </div>
    </div>

    <div className="progress-bar" style={{ marginBottom: '8px' }}>
      <div
        className="progress-fill"
        style={{ width: `${download.progress}%` }}
      />
    </div>

    <div style={{
      display: 'flex',
      justifyContent: 'space-between',
      fontSize: '12px',
      color: '#999'
    }}>
      <span>{download.progress.toFixed(1)}%</span>
      <span>
        {formatSpeed(download.download_speed)} • ETA: {formatETA(download.eta_seconds)}
      </span>
    </div>

    {download.error_message && (
      <div style={{
        marginTop: '8px',
        padding: '8px',
        background: 'rgba(244, 67, 54, 0.1)',
        border: '1px solid rgba(244, 67, 54, 0.3)',
        borderRadius: '4px',
        fontSize: '12px',
        color: '#f44336'
      }}>
        Error: {download.error_message}
      </div>
    )}
  </div>
))

DownloadItem.displayName = 'DownloadItem'

const ProgressPanel: React.FC = () => {
  const [downloads, setDownloads] = useState<DownloadStatusResponse[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Fetch active downloads on mount
    const fetchDownloads = async () => {
      try {
        const data = await downloadsApi.getActiveDownloads()
        setDownloads(data.downloads)
      } catch (error) {
        console.error('Failed to fetch downloads:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchDownloads()

    // Listen for progress updates via WebSocket
    const handleProgressUpdate = (data: ProgressUpdate) => {
      setDownloads(prev => {
        const index = prev.findIndex(d => d.task_id === data.task_id)
        if (index >= 0) {
          const updated = [...prev]
          updated[index] = { ...updated[index], ...data }
          return updated
        }
        return prev
      })
    }

    progressWS.on('progress', handleProgressUpdate)

    // Poll for updates every 5 seconds as backup
    const interval = setInterval(fetchDownloads, 5000)

    return () => {
      progressWS.off('progress', handleProgressUpdate)
      clearInterval(interval)
    }
  }, [])

  if (isLoading) {
    return (
      <div className="card">
        <h2 style={{ marginBottom: '16px', fontSize: '20px' }}>Active Downloads</h2>
        <div className="spinner"></div>
      </div>
    )
  }

  if (downloads.length === 0) {
    return (
      <div className="card">
        <h2 style={{ marginBottom: '16px', fontSize: '20px' }}>Active Downloads</h2>
        <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
          <Activity size={48} style={{ marginBottom: '12px', opacity: 0.5 }} />
          <p>No active downloads</p>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <h2 style={{ marginBottom: '16px', fontSize: '20px' }}>
        Active Downloads ({downloads.length})
      </h2>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {downloads.map((download) => (
          <DownloadItem key={download.task_id} download={download} />
        ))}
      </div>
    </div>
  )
}

export default ProgressPanel
