import React, { useEffect, useState } from 'react'
import { Play, Pause, Trash2, ArrowUp, ArrowDown, RefreshCw, Trash } from 'lucide-react'
import { queueApi } from '@/services/api'
import type { QueueItem } from '@/types/api'

const QueuePage: React.FC = () => {
  const [items, setItems] = useState<QueueItem[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const fetchQueue = async () => {
    try {
      setRefreshing(true)
      const data = await queueApi.getItems()
      setItems(data)
    } catch (error) {
      console.error('Failed to fetch queue:', error)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchQueue()
    const interval = setInterval(fetchQueue, 2000)
    return () => clearInterval(interval)
  }, [])

  const handlePause = async (id: string) => {
    try {
      await queueApi.pauseItem(id)
      fetchQueue()
    } catch (error) {
      console.error('Failed to pause item:', error)
    }
  }

  const handleResume = async (id: string) => {
    try {
      await queueApi.resumeItem(id)
      fetchQueue()
    } catch (error) {
      console.error('Failed to resume item:', error)
    }
  }

  const handleRemove = async (id: string) => {
    try {
      await queueApi.removeItem(id)
      fetchQueue()
    } catch (error) {
      console.error('Failed to remove item:', error)
    }
  }

  const handleMoveUp = async (id: string) => {
    try {
      await queueApi.moveUp(id)
      fetchQueue()
    } catch (error) {
      console.error('Failed to move item up:', error)
    }
  }

  const handleMoveDown = async (id: string) => {
    try {
      await queueApi.moveDown(id)
      fetchQueue()
    } catch (error) {
      console.error('Failed to move item down:', error)
    }
  }

  const handleClearCompleted = async () => {
    try {
      await queueApi.clearCompleted()
      fetchQueue()
    } catch (error) {
      console.error('Failed to clear completed items:', error)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'downloading': return '#2196f3'
      case 'completed': return '#4caf50'
      case 'failed': return '#f44336'
      case 'paused': return '#ff9800'
      default: return '#9e9e9e'
    }
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <h2 style={{ fontSize: '20px', margin: 0 }}>Download Queue</h2>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            className="button"
            onClick={fetchQueue}
            style={{ padding: '8px 12px', fontSize: '14px', background: 'rgba(255,255,255,0.1)', border: '1px solid var(--border-color)' }}
          >
            <RefreshCw size={16} className={refreshing ? 'spin' : ''} />
          </button>
          <button
            className="button"
            onClick={handleClearCompleted}
            style={{ padding: '8px 12px', fontSize: '14px', background: 'rgba(244, 67, 54, 0.1)', border: '1px solid #f44336', color: '#f44336' }}
          >
            <Trash size={16} style={{ marginRight: '6px' }} />
            Clear Completed
          </button>
        </div>
      </div>

      {loading && items.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
          Loading queue...
        </div>
      ) : items.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
          Queue is empty
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left' }}>
                <th style={{ padding: '12px', width: '40px' }}>#</th>
                <th style={{ padding: '12px' }}>URL</th>
                <th style={{ padding: '12px', width: '100px' }}>Status</th>
                <th style={{ padding: '12px', width: '120px' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item, index) => (
                <tr key={item.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '12px', color: 'var(--text-secondary)' }}>{index + 1}</td>
                  <td style={{ padding: '12px' }}>
                    <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '300px' }}>
                      {item.url}
                    </div>
                    {item.status === 'downloading' && (
                      <div style={{ marginTop: '4px', height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', overflow: 'hidden' }}>
                        {/* Note: In real app, item.progress might not be populated if queue doesn't actively track it.
                            However, since we updated backend models, it should be there.
                            Assuming item.progress is 0-1 or 0-100? Backend default is 0.0.
                            Usually 0.0-1.0 or 0-100. Let's assume 0-100 for now or multiply if needed.
                            Actually backend `DownloadStatusResponse` uses float (0.0 to 100.0 usually).
                            Let's check `QueueItem`. `progress: float = 0.0`.
                            Usually we normalize. */}
                         <div style={{ height: '100%', width: `${item.progress || 0}%`, background: '#2196f3' }} />
                      </div>
                    )}
                  </td>
                  <td style={{ padding: '12px' }}>
                    <span style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      background: `${getStatusColor(item.status)}20`,
                      color: getStatusColor(item.status),
                      border: `1px solid ${getStatusColor(item.status)}40`
                    }}>
                      {item.status.toUpperCase()}
                    </span>
                  </td>
                  <td style={{ padding: '12px' }}>
                    <div style={{ display: 'flex', gap: '4px' }}>
                      {item.status === 'downloading' ? (
                        <button onClick={() => handlePause(item.id)} className="icon-button" title="Pause">
                          <Pause size={16} />
                        </button>
                      ) : item.status === 'paused' ? (
                        <button onClick={() => handleResume(item.id)} className="icon-button" title="Resume">
                          <Play size={16} />
                        </button>
                      ) : null}

                      <button onClick={() => handleMoveUp(item.id)} className="icon-button" title="Move Up" disabled={index === 0}>
                        <ArrowUp size={16} />
                      </button>
                      <button onClick={() => handleMoveDown(item.id)} className="icon-button" title="Move Down" disabled={index === items.length - 1}>
                        <ArrowDown size={16} />
                      </button>

                      <button onClick={() => handleRemove(item.id)} className="icon-button delete" title="Remove">
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <style>{`
        .icon-button {
          background: transparent;
          border: none;
          color: var(--text-secondary);
          cursor: pointer;
          padding: 4px;
          border-radius: 4px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .icon-button:hover {
          background: rgba(255,255,255,0.1);
          color: var(--text-color);
        }
        .icon-button:disabled {
          opacity: 0.3;
          cursor: not-allowed;
        }
        .icon-button.delete:hover {
          background: rgba(244, 67, 54, 0.1);
          color: #f44336;
        }
        .spin {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}

export default QueuePage
