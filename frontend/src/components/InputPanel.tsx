import React, { useState } from 'react'
import { Download, Loader2, ListPlus } from 'lucide-react'
import { downloadsApi, queueApi } from '@/services/api'
import type { DownloadOptions } from '@/types/api'
import AdvancedSettings from './AdvancedSettings'

const InputPanel: React.FC = () => {
  const [urls, setUrls] = useState('')
  const [isDownloading, setIsDownloading] = useState(false)
  const [options, setOptions] = useState<Partial<DownloadOptions>>({
    download_images: true,
    download_videos: true,
    download_compressed: true,
    download_documents: true,
  })
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null)

  const handleDownload = async () => {
    const urlList = urls.split('\n').filter(url => url.trim())
    
    if (urlList.length === 0) {
      setMessage({ text: 'Please enter at least one URL', type: 'error' })
      return
    }

    setIsDownloading(true)
    setMessage(null)

    try {
      const responses = await downloadsApi.startDownload({
        urls: urlList,
        options,
      })

      const successCount = responses.filter(r => r.status === 'started').length
      const failCount = responses.length - successCount

      if (failCount === 0) {
        setMessage({ 
          text: `Started ${successCount} download(s) successfully!`, 
          type: 'success' 
        })
        setUrls('')
      } else {
        setMessage({ 
          text: `Started ${successCount} download(s). ${failCount} failed to start.`, 
          type: 'error' 
        })
      }
    } catch (error) {
      console.error('Download error:', error)
      setMessage({ 
        text: 'Failed to start downloads. Please check the console for details.', 
        type: 'error' 
      })
    } finally {
      setIsDownloading(false)
    }
  }

  const handleAddToQueue = async () => {
    const urlList = urls.split('\n').filter(url => url.trim())

    if (urlList.length === 0) {
      setMessage({ text: 'Please enter at least one URL', type: 'error' })
      return
    }

    setIsDownloading(true)
    setMessage(null)

    try {
      await queueApi.addItem({
        urls: urlList,
        options,
      })

      setMessage({
        text: `Added ${urlList.length} items to queue successfully!`,
        type: 'success'
      })
      setUrls('')
    } catch (error) {
      console.error('Queue error:', error)
      setMessage({
        text: 'Failed to add items to queue.',
        type: 'error'
      })
    } finally {
      setIsDownloading(false)
    }
  }

  const toggleOption = (key: keyof DownloadOptions) => {
    setOptions(prev => ({ ...prev, [key]: !prev[key] }))
  }

  return (
    <div className="card">
      <h2 style={{ marginBottom: '16px', fontSize: '20px' }}>Download Media</h2>
      
      <div style={{ marginBottom: '16px' }}>
        <label className="label">URLs (one per line)</label>
        <textarea
          className="input textarea"
          placeholder="https://example.com/media&#10;https://example.com/gallery"
          value={urls}
          onChange={(e) => setUrls(e.target.value)}
          disabled={isDownloading}
        />
      </div>

      <div style={{ marginBottom: '16px' }}>
        <label className="label">Download Options</label>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '12px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              className="checkbox"
              checked={options.download_images}
              onChange={() => toggleOption('download_images')}
              disabled={isDownloading}
            />
            <span>Images</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              className="checkbox"
              checked={options.download_videos}
              onChange={() => toggleOption('download_videos')}
              disabled={isDownloading}
            />
            <span>Videos</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              className="checkbox"
              checked={options.download_compressed}
              onChange={() => toggleOption('download_compressed')}
              disabled={isDownloading}
            />
            <span>Archives</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              className="checkbox"
              checked={options.download_documents}
              onChange={() => toggleOption('download_documents')}
              disabled={isDownloading}
            />
            <span>Documents</span>
          </label>
        </div>
      </div>

      <AdvancedSettings
        options={options}
        onChange={setOptions}
        disabled={isDownloading}
      />

      {message && (
        <div style={{
          padding: '12px',
          marginBottom: '16px',
          borderRadius: '6px',
          background: message.type === 'success' ? 'rgba(76, 175, 80, 0.2)' : 'rgba(244, 67, 54, 0.2)',
          border: `1px solid ${message.type === 'success' ? '#4caf50' : '#f44336'}`,
          color: message.type === 'success' ? '#4caf50' : '#f44336',
        }}>
          {message.text}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
        <button
          className="button"
          onClick={handleDownload}
          disabled={isDownloading || !urls.trim()}
          style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
        >
          {isDownloading ? (
            <>
              <Loader2 size={20} style={{ animation: 'spin 1s linear infinite' }} />
              Starting...
            </>
          ) : (
            <>
              <Download size={20} />
              Start Download
            </>
          )}
        </button>

        <button
          className="button"
          onClick={handleAddToQueue}
          disabled={isDownloading || !urls.trim()}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            border: '1px solid var(--border-color)'
          }}
        >
          <ListPlus size={20} />
          Add to Queue
        </button>
      </div>
    </div>
  )
}

export default InputPanel
