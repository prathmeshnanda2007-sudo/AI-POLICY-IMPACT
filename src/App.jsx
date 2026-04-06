import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Simulator from './pages/Simulator'
import Results from './pages/Results'
import Scenarios from './pages/Scenarios'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Signup from './pages/Signup'

// Loading spinner shown while verifying token on app startup
function LoadingScreen() {
  return (
    <div className="min-h-screen bg-dark-500 flex items-center justify-center">
      <div className="text-center">
        <div className="w-12 h-12 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-sm text-gray-400">Verifying session...</p>
      </div>
    </div>
  )
}

// Protected route wrapper — redirects to login if not authenticated
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  if (loading) return <LoadingScreen />
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return children
}

// Public route wrapper — redirects to dashboard if already authenticated
function PublicRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  if (loading) return <LoadingScreen />
  if (isAuthenticated) return <Navigate to="/" replace />
  return children
}

function AppRoutes() {
  const { isAuthenticated, loading, logout } = useAuth()

  if (loading) return <LoadingScreen />

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/landing" element={
        <PublicRoute><Landing /></PublicRoute>
      } />
      <Route path="/login" element={
        <PublicRoute><Login /></PublicRoute>
      } />
      <Route path="/signup" element={
        <PublicRoute><Signup /></PublicRoute>
      } />

      {/* Protected routes */}
      <Route path="/" element={
        <ProtectedRoute>
          <Layout onLogout={logout}>
            <Dashboard />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/simulator" element={
        <ProtectedRoute>
          <Layout onLogout={logout}>
            <Simulator />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/results" element={
        <ProtectedRoute>
          <Layout onLogout={logout}>
            <Results />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/scenarios" element={
        <ProtectedRoute>
          <Layout onLogout={logout}>
            <Scenarios />
          </Layout>
        </ProtectedRoute>
      } />

      {/* Catch all — redirect based on auth state */}
      <Route path="*" element={
        isAuthenticated ? <Navigate to="/" replace /> : <Navigate to="/login" replace />
      } />
    </Routes>
  )
}

export default function App() {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  )
}
