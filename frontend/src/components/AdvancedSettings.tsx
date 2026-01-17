import React, { useState } from 'react'
import { Settings, ChevronDown, ChevronUp } from 'lucide-react'
import type { DownloadOptions, YtDlpOptions } from '@/types/api'

interface AdvancedSettingsProps {
  options: Partial<DownloadOptions>
  onChange: (options: Partial<DownloadOptions>) => void
  disabled?: boolean
}

const AdvancedSettings: React.FC<AdvancedSettingsProps> = ({ options, onChange, disabled }) => {
  const [isOpen, setIsOpen] = useState(false)

  const handleYtDlpChange = (updates: Partial<YtDlpOptions>) => {
    onChange({
      ...options,
      ytdlp_options: {
        ...options.ytdlp_options,
        // Provide defaults if undefined
        format_selector: 'best',
        merge_output_format: 'mp4',
        embed_thumbnail: true,
        embed_metadata: true,
        download_subtitles: false,
        subtitle_languages: 'en',
        ...updates
      } as YtDlpOptions
    })
  }

  const handleChange = (field: keyof DownloadOptions, value: any) => {
    onChange({ ...options, [field]: value })
  }

  return (
    <div style={{ marginBottom: '16px', border: '1px solid var(--border-color)', borderRadius: '8px', overflow: 'hidden' }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px',
          background: 'rgba(255, 255, 255, 0.05)',
          border: 'none',
          color: 'var(--text-color)',
          cursor: 'pointer',
          fontSize: '14px',
          fontWeight: 500
        }}
        type="button"
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Settings size={18} />
          <span>Advanced Settings</span>
        </div>
        {isOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
      </button>

      {isOpen && (
        <div style={{ padding: '16px', background: 'rgba(0, 0, 0, 0.1)' }}>
          {/* Network Settings */}
          <div style={{ marginBottom: '16px' }}>
            <h3 style={{ fontSize: '14px', marginBottom: '8px', color: 'var(--text-secondary)' }}>Network</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div>
                <label className="label" style={{ fontSize: '12px' }}>Proxy URL</label>
                <input
                  type="text"
                  className="input"
                  placeholder="http://user:pass@host:port"
                  value={options.proxy_url || ''}
                  onChange={(e) => handleChange('proxy_url', e.target.value)}
                  disabled={disabled}
                />
              </div>
              <div>
                <label className="label" style={{ fontSize: '12px' }}>Bandwidth Limit (KB/s)</label>
                <input
                  type="number"
                  className="input"
                  placeholder="0 (Unlimited)"
                  value={options.bandwidth_limit_kbps || ''}
                  onChange={(e) => handleChange('bandwidth_limit_kbps', parseInt(e.target.value) || 0)}
                  disabled={disabled}
                />
              </div>
            </div>
          </div>

          {/* Filters */}
          <div style={{ marginBottom: '16px' }}>
            <h3 style={{ fontSize: '14px', marginBottom: '8px', color: 'var(--text-secondary)' }}>Filters</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div>
                <label className="label" style={{ fontSize: '12px' }}>Date From</label>
                <input
                  type="date"
                  className="input"
                  value={options.date_from || ''}
                  onChange={(e) => handleChange('date_from', e.target.value)}
                  disabled={disabled}
                />
              </div>
              <div>
                <label className="label" style={{ fontSize: '12px' }}>Date To</label>
                <input
                  type="date"
                  className="input"
                  value={options.date_to || ''}
                  onChange={(e) => handleChange('date_to', e.target.value)}
                  disabled={disabled}
                />
              </div>
              <div>
                <label className="label" style={{ fontSize: '12px' }}>Min Size (MB)</label>
                <input
                  type="number"
                  className="input"
                  placeholder="0"
                  value={options.min_file_size ? options.min_file_size / (1024 * 1024) : ''}
                  onChange={(e) => handleChange('min_file_size', (parseInt(e.target.value) || 0) * 1024 * 1024)}
                  disabled={disabled}
                />
              </div>
              <div>
                <label className="label" style={{ fontSize: '12px' }}>Max Size (MB)</label>
                <input
                  type="number"
                  className="input"
                  placeholder="0"
                  value={options.max_file_size ? options.max_file_size / (1024 * 1024) : ''}
                  onChange={(e) => handleChange('max_file_size', (parseInt(e.target.value) || 0) * 1024 * 1024)}
                  disabled={disabled}
                />
              </div>
            </div>
          </div>

          {/* Universal Downloader (yt-dlp) */}
          <div>
            <h3 style={{ fontSize: '14px', marginBottom: '8px', color: 'var(--text-secondary)' }}>Universal Downloader (yt-dlp)</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
              <div>
                <label className="label" style={{ fontSize: '12px' }}>Format</label>
                <select
                  className="input"
                  value={options.ytdlp_options?.format_selector || 'best'}
                  onChange={(e) => handleYtDlpChange({ format_selector: e.target.value })}
                  disabled={disabled}
                >
                  <option value="best">Best Video + Audio</option>
                  <option value="bestvideo">Best Video</option>
                  <option value="bestaudio">Best Audio</option>
                  <option value="mp4">MP4</option>
                </select>
              </div>
              <div>
                <label className="label" style={{ fontSize: '12px' }}>Browser Cookies</label>
                <select
                  className="input"
                  value={options.ytdlp_options?.cookies_from_browser || ''}
                  onChange={(e) => handleYtDlpChange({ cookies_from_browser: e.target.value || undefined })}
                  disabled={disabled}
                >
                  <option value="">None</option>
                  <option value="chrome">Chrome</option>
                  <option value="firefox">Firefox</option>
                  <option value="edge">Edge</option>
                  <option value="opera">Opera</option>
                  <option value="brave">Brave</option>
                </select>
              </div>
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  className="checkbox"
                  checked={options.ytdlp_options?.download_subtitles || false}
                  onChange={(e) => handleYtDlpChange({ download_subtitles: e.target.checked })}
                  disabled={disabled}
                />
                <span>Download Subtitles</span>
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  className="checkbox"
                  checked={options.ytdlp_options?.embed_thumbnail ?? true}
                  onChange={(e) => handleYtDlpChange({ embed_thumbnail: e.target.checked })}
                  disabled={disabled}
                />
                <span>Embed Thumbnail</span>
              </label>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AdvancedSettings
