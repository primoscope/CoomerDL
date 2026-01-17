/**
 * API types and interfaces
 */

export enum DownloadStatus {
  PENDING = 'pending',
  DOWNLOADING = 'downloading',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
  SKIPPED = 'skipped',
}

export interface YtDlpOptions {
  format_selector: string
  merge_output_format: string
  embed_thumbnail: boolean
  embed_metadata: boolean
  download_subtitles: boolean
  subtitle_languages: string
  cookies_from_browser?: string
  ffmpeg_location?: string
  rate_limit?: string
}

export interface DownloadOptions {
  download_images: boolean
  download_videos: boolean
  download_compressed: boolean
  download_documents: boolean
  max_retries: number
  retry_interval: number
  chunk_size: number
  timeout: number
  min_file_size: number
  max_file_size: number
  date_from?: string
  date_to?: string
  excluded_extensions: string[]
  proxy_type: string
  proxy_url: string
  user_agent?: string
  bandwidth_limit_kbps: number
  connection_timeout: number
  read_timeout: number
  ytdlp_options?: YtDlpOptions
}

export interface QueueItem {
  id: string
  url: string
  status: DownloadStatus
  priority: number
  position: number
  progress: number
  options?: Partial<DownloadOptions>
  created_at: string
  updated_at: string
}

export interface DownloadRequest {
  urls: string[]
  download_folder?: string
  options?: Partial<DownloadOptions>
}

export interface DownloadResponse {
  task_id: string
  status: string
  message: string
}

export interface DownloadStatusResponse {
  task_id: string
  status: DownloadStatus
  url: string
  progress: number
  current_file?: string
  total_files: number
  completed_files: number
  failed_files: number
  download_speed: number
  eta_seconds?: number
  error_message?: string
  created_at: string
  updated_at: string
}

export interface ProgressUpdate {
  task_id: string
  status: DownloadStatus
  progress: number
  current_file?: string
  download_speed: number
  eta_seconds?: number
}

export interface LogMessage {
  timestamp: string
  level: string
  message: string
}

export interface WebSocketMessage {
  type: 'progress' | 'log'
  timestamp: string
  [key: string]: any
}
