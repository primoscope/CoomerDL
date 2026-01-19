
export const formatSpeed = (bytesPerSecond: number): string => {
  if (bytesPerSecond < 1024) return `${bytesPerSecond.toFixed(0)} B/s`
  if (bytesPerSecond < 1024 * 1024) return `${(bytesPerSecond / 1024).toFixed(1)} KB/s`
  return `${(bytesPerSecond / (1024 * 1024)).toFixed(1)} MB/s`
}

export const formatETA = (seconds?: number): string => {
  if (!seconds) return 'Calculating...'
  if (seconds < 60) return `${Math.round(seconds)}s`
  if (seconds < 3600) return `${Math.round(seconds / 60)}m`
  return `${Math.round(seconds / 3600)}h`
}

export const getStatusColor = (status: string): string => {
  switch (status) {
    case 'downloading': return '#667eea'
    case 'completed': return '#4caf50'
    case 'failed': return '#f44336'
    case 'cancelled': return '#999'
    default: return '#ff9800'
  }
}
