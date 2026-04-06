import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Simulator from './pages/Simulator'
import Results from './pages/Results'
import Scenarios from './pages/Scenarios'
import Landing from './pages/Landing'

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = React.useState(() => {
    return localStorage.getItem('policyai_auth') === 'true'
  })

  const handleLogin = () => {
    localStorage.setItem('policyai_auth', 'true')
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    localStorage.removeItem('policyai_auth')
    setIsAuthenticated(false)
  }

  if (!isAuthenticated) {
    return (
      <Router>
        <Landing onLogin={handleLogin} />
      </Router>
    )
  }

  return (
    <Router>
      <Layout onLogout={handleLogout}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/simulator" element={<Simulator />} />
          <Route path="/results" element={<Results />} />
          <Route path="/scenarios" element={<Scenarios />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </Router>
  )
}
