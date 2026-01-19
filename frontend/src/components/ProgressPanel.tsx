import React, { useEffect, useState } from 'react'
import { Activity } from 'lucide-react'
import { downloadsApi } from '@/services/api'
import { progressWS } from '@/services/websocket'
import type { DownloadStatusResponse, ProgressUpdate } from '@/types/api'
import DownloadItem from './DownloadItem'

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
    const handleProgressUpdate = (data: unknown) => {
      const update = data as ProgressUpdate

      setDownloads(prev => {
        const index = prev.findIndex(d => d.task_id === update.task_id)
        if (index >= 0) {
          const updated = [...prev]
          updated[index] = { ...updated[index], ...update }
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
          <DownloadItem
            key={download.task_id}
            download={download}
          />
        ))}
      </div>
    </div>
  )
}

export default ProgressPanel
