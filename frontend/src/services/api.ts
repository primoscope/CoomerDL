/**
 * API client for CoomerDL backend
 */
import axios from 'axios'
import type {
  DownloadRequest,
  DownloadResponse,
  DownloadStatusResponse,
  QueueItem,
  DownloadOptions,
} from '@/types/api'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor for auth tokens (if needed)
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const downloadsApi = {
  /**
   * Start one or more downloads
   */
  startDownload: async (request: DownloadRequest): Promise<DownloadResponse[]> => {
    const response = await apiClient.post('/downloads/start', request)
    return response.data
  },

  /**
   * Get status of a download
   */
  getDownloadStatus: async (taskId: string): Promise<DownloadStatusResponse> => {
    const response = await apiClient.get(`/downloads/status/${taskId}`)
    return response.data
  },

  /**
   * Cancel a download
   */
  cancelDownload: async (taskId: string): Promise<{ message: string }> => {
    const response = await apiClient.post(`/downloads/cancel/${taskId}`)
    return response.data
  },

  /**
   * Get all active downloads
   */
  getActiveDownloads: async (): Promise<{
    count: number
    downloads: DownloadStatusResponse[]
  }> => {
    const response = await apiClient.get('/downloads/active')
    return response.data
  },
}

export const queueApi = {
  getItems: async (): Promise<QueueItem[]> => {
    const response = await apiClient.get('/queue/')
    return response.data
  },

  addItem: async (request: { urls: string[], options?: Partial<DownloadOptions>, priority?: number }): Promise<QueueItem[]> => {
    const response = await apiClient.post('/queue/add', request)
    return response.data
  },

  pauseItem: async (itemId: string): Promise<{ message: string }> => {
    const response = await apiClient.post(`/queue/pause/${itemId}`)
    return response.data
  },

  resumeItem: async (itemId: string): Promise<{ message: string }> => {
    const response = await apiClient.post(`/queue/resume/${itemId}`)
    return response.data
  },

  removeItem: async (itemId: string): Promise<{ message: string }> => {
    const response = await apiClient.delete(`/queue/${itemId}`)
    return response.data
  },

  clearCompleted: async (): Promise<{ message: string }> => {
    const response = await apiClient.post('/queue/clear')
    return response.data
  },

  moveUp: async (itemId: string): Promise<{ message: string }> => {
    const response = await apiClient.post(`/queue/reorder/up/${itemId}`)
    return response.data
  },

  moveDown: async (itemId: string): Promise<{ message: string }> => {
    const response = await apiClient.post(`/queue/reorder/down/${itemId}`)
    return response.data
  }
}

export const healthApi = {
  /**
   * Check API health
   */
  check: async (): Promise<{ status: string; service: string; version: string }> => {
    const response = await apiClient.get('/health')
    return response.data
  },
}

export default apiClient
