import React, { memo } from 'react'
import type { DownloadStatusResponse } from '../types/api'
import { formatSpeed, formatETA, getStatusColor } from '../utils/formatters'

interface DownloadItemProps {
  download: DownloadStatusResponse
}

const DownloadItem: React.FC<DownloadItemProps> = ({ download }) => {
  return (
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
  )
}

export default memo(DownloadItem)
