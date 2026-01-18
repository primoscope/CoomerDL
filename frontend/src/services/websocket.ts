/**
 * WebSocket service for real-time updates
 */

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 
  (window.location.protocol === 'https:' ? 'wss:' : 'ws:') + 
  '//' + window.location.host + '/ws'

export class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 3000
  private listeners: Map<string, Set<(data: any) => void>> = new Map()
  private heartbeatInterval: NodeJS.Timeout | null = null

  constructor(private endpoint: string) {}

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const url = `${WS_BASE_URL}${this.endpoint}`
        console.log(`Connecting to WebSocket: ${url}`)
        
        this.ws = new WebSocket(url)

        this.ws.onopen = () => {
          console.log(`WebSocket connected: ${this.endpoint}`)
          this.reconnectAttempts = 0
          this.startHeartbeat()
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            this.notifyListeners(data.type || 'message', data)
          } catch (error) {
            console.error('Error parsing WebSocket message:', error)
          }
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          reject(error)
        }

        this.ws.onclose = () => {
          console.log('WebSocket disconnected')
          this.stopHeartbeat()
          this.attemptReconnect()
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  private startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send('ping')
      }
    }, 30000) // Send ping every 30 seconds
  }

  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
      
      setTimeout(() => {
        this.connect().catch(console.error)
      }, this.reconnectDelay * this.reconnectAttempts)
    } else {
      console.error('Max reconnection attempts reached')
    }
  }

  on(event: string, callback: (data: any) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)!.add(callback)
  }

  off(event: string, callback: (data: any) => void) {
    const listeners = this.listeners.get(event)
    if (listeners) {
      listeners.delete(callback)
    }
  }

  private notifyListeners(event: string, data: any) {
    const listeners = this.listeners.get(event)
    if (listeners) {
      listeners.forEach((callback) => callback(data))
    }
  }

  send(data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(typeof data === 'string' ? data : JSON.stringify(data))
    } else {
      console.warn('WebSocket is not connected')
    }
  }

  disconnect() {
    this.stopHeartbeat()
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.listeners.clear()
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

// Create singleton instances
export const progressWS = new WebSocketService('/progress')
export const logsWS = new WebSocketService('/logs')
