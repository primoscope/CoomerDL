import React, { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom'
import { Download, Activity, List, Home } from 'lucide-react'
import HomePage from './pages/HomePage'
import QueuePage from './pages/QueuePage'
import { healthApi } from './services/api'
import { progressWS, logsWS } from './services/websocket'
import './styles/index.css'

function App() {
  const [isBackendHealthy, setIsBackendHealthy] = useState(false)
  const [isConnecting, setIsConnecting] = useState(true)

  useEffect(() => {
    // Check backend health
    const checkHealth = async () => {
      try {
        const health = await healthApi.check()
        setIsBackendHealthy(health.status === 'healthy')
        console.log('Backend health check:', health)
      } catch (error) {
        console.error('Backend health check failed:', error)
        setIsBackendHealthy(false)
      } finally {
        setIsConnecting(false)
      }
    }

    checkHealth()

    // Connect to WebSockets
    progressWS.connect().catch(console.error)
    logsWS.connect().catch(console.error)

    return () => {
      progressWS.disconnect()
      logsWS.disconnect()
    }
  }, [])

  if (isConnecting) {
    return (
      <div className="app-container">
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column',
          alignItems: 'center', 
          justifyContent: 'center', 
          height: '100vh',
          gap: '20px'
        }}>
          <div className="spinner"></div>
          <p>Connecting to backend...</p>
        </div>
      </div>
    )
  }

  if (!isBackendHealthy) {
    return (
      <div className="app-container">
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column',
          alignItems: 'center', 
          justifyContent: 'center', 
          height: '100vh',
          gap: '20px',
          padding: '20px',
          textAlign: 'center'
        }}>
          <Activity size={64} color="#f44336" />
          <h1>Backend Unavailable</h1>
          <p>Unable to connect to the CoomerDL backend server.</p>
          <p style={{ color: '#999' }}>Please make sure the backend is running on port 8080.</p>
          <button 
            className="button" 
            onClick={() => window.location.reload()}
          >
            Retry Connection
          </button>
        </div>
      </div>
    )
  }

  return (
    <Router>
      <div className="app-container">
        <header style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          padding: '20px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.3)'
        }}>
          <div style={{
            maxWidth: '1400px',
            margin: '0 auto',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <Download size={32} />
              <div>
                <h1 style={{ margin: 0, fontSize: '24px' }}>CoomerDL</h1>
                <p style={{ margin: 0, opacity: 0.9, fontSize: '14px' }}>
                  Universal Media Downloader
                </p>
              </div>
            </div>

            <nav style={{ display: 'flex', gap: '20px' }}>
              <NavLink
                to="/"
                className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}
                style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'white', textDecoration: 'none', padding: '8px 16px', borderRadius: '20px', transition: 'background 0.2s' }}
              >
                <Home size={18} />
                <span>Home</span>
              </NavLink>
              <NavLink
                to="/queue"
                className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}
                style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'white', textDecoration: 'none', padding: '8px 16px', borderRadius: '20px', transition: 'background 0.2s' }}
              >
                <List size={18} />
                <span>Queue</span>
              </NavLink>
            </nav>
          </div>
        </header>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/queue" element={<QueuePage />} />
          </Routes>
        </main>

        <footer style={{
          padding: '20px',
          textAlign: 'center',
          borderTop: '1px solid var(--border-color)',
          color: 'var(--text-secondary)',
          fontSize: '14px'
        }}>
          <p>CoomerDL v2.0.0 - Web Edition</p>
          <p style={{ marginTop: '5px' }}>
            <a
              href="https://github.com/primoscope/CoomerDL"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: 'var(--primary-color)', textDecoration: 'none' }}
            >
              GitHub Repository
            </a>
          </p>
        </footer>
      </div>
      <style>{`
        .nav-link:hover {
          background: rgba(255, 255, 255, 0.1);
        }
        .nav-link.active {
          background: rgba(255, 255, 255, 0.2);
          font-weight: 500;
        }
      `}</style>
    </Router>
  )
}

export default App
