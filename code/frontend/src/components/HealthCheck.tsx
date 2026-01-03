import { useEffect, useState } from 'react'
import './HealthCheck.css'

const BACKEND_URL = 'http://localhost:8000'

interface HealthStatus {
  status: 'healthy' | 'unhealthy' | 'unknown'
  message: string
}

function HealthCheck() {
  const [health, setHealth] = useState<HealthStatus>({
    status: 'unknown',
    message: 'Checking...'
  })

  useEffect(() => {
    checkHealth()
  }, [])

  const checkHealth = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/health`)
      const data = await response.json()
      setHealth({
        status: data.status === 'healthy' ? 'healthy' : 'unhealthy',
        message: data.message
      })
    } catch (error) {
      setHealth({
        status: 'unhealthy',
        message: 'Backend is not reachable'
      })
    }
  }

  return (
    <div className="health-check">
      <h2>Backend Status</h2>
      <div className={`status-indicator ${health.status}`}>
        <span className="status-dot"></span>
        <span className="status-text">{health.status.toUpperCase()}</span>
      </div>
      <p>{health.message}</p>
      <button onClick={checkHealth}>Refresh</button>
    </div>
  )
}

export default HealthCheck
