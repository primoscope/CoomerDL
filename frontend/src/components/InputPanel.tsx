import React, { useState } from 'react'
import { Download, Loader2 } from 'lucide-react'
import { downloadsApi } from '@/services/api'
import type { DownloadOptions } from '@/types/api'

const InputPanel: React.FC = () => {
  const [urls, setUrls] = useState('')
  const [isDownloading, setIsDownloading] = useState(false)
  const [downloadImages, setDownloadImages] = useState(true)
  const [downloadVideos, setDownloadVideos] = useState(true)
  const [downloadCompressed, setDownloadCompressed] = useState(true)
  const [downloadDocuments, setDownloadDocuments] = useState(true)
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
      const options: Partial<DownloadOptions> = {
        download_images: downloadImages,
        download_videos: downloadVideos,
        download_compressed: downloadCompressed,
        download_documents: downloadDocuments,
      }

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
              checked={downloadImages}
              onChange={(e) => setDownloadImages(e.target.checked)}
              disabled={isDownloading}
            />
            <span>Images</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              className="checkbox"
              checked={downloadVideos}
              onChange={(e) => setDownloadVideos(e.target.checked)}
              disabled={isDownloading}
            />
            <span>Videos</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              className="checkbox"
              checked={downloadCompressed}
              onChange={(e) => setDownloadCompressed(e.target.checked)}
              disabled={isDownloading}
            />
            <span>Archives</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              className="checkbox"
              checked={downloadDocuments}
              onChange={(e) => setDownloadDocuments(e.target.checked)}
              disabled={isDownloading}
            />
            <span>Documents</span>
          </label>
        </div>
      </div>

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

      <button
        className="button"
        onClick={handleDownload}
        disabled={isDownloading || !urls.trim()}
        style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
      >
        {isDownloading ? (
          <>
            <Loader2 size={20} style={{ animation: 'spin 1s linear infinite' }} />
            Starting Downloads...
          </>
        ) : (
          <>
            <Download size={20} />
            Start Download
          </>
        )}
      </button>
    </div>
  )
}

export default InputPanel
