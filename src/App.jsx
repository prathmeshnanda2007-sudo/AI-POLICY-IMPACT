import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Layout from './components/Layout'
import PageWrapper from './components/PageWrapper'
import Dashboard from './pages/Dashboard'
import Simulator from './pages/Simulator'
import Results from './pages/Results'
import Scenarios from './pages/Scenarios'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Signup from './pages/Signup'

// ── Loading screen shown while JWT is being verified on startup
function LoadingScreen() {
  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="relative w-14 h-14">
          <div className="absolute inset-0 rounded-full border-2 border-primary-500/20" />
          <div className="absolute inset-0 rounded-full border-2 border-primary-500 border-t-transparent animate-spin" />
        </div>
        <p className="text-sm text-white/40 tracking-widest uppercase">Verifying session</p>
      </div>
    </div>
  )
}

// ── Smart root: Landing for guests, Dashboard for authenticated users
function RootRoute({ logout }) {
  const { isAuthenticated, loading } = useAuth()
  if (loading) return <LoadingScreen />
  if (isAuthenticated) {
    return (
      <Layout onLogout={logout}>
        <PageWrapper><Dashboard /></PageWrapper>
      </Layout>
    )
  }
  return <Landing />
}

// ── ProtectedRoute: bounce unauthenticated users back to /
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  if (loading) return <LoadingScreen />
  if (!isAuthenticated) return <Navigate to="/" replace />
  return children
}

// ── PublicRoute: bounce authenticated users to /dashboard
function PublicRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  if (loading) return <LoadingScreen />
  if (isAuthenticated) return <Navigate to="/dashboard" replace />
  return children
}

function AppRoutes() {
  const { logout } = useAuth()
  const location = useLocation()

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        {/* ── Root: Landing (guest) OR Dashboard (authenticated) */}
        <Route path="/" element={<RootRoute logout={logout} />} />

      {/* ── Auth pages (redirect to /dashboard if already logged in) */}
      <Route path="/login"  element={<PublicRoute><Login /></PublicRoute>} />
      <Route path="/signup" element={<PublicRoute><Signup /></PublicRoute>} />

      {/* ── Protected app routes */}
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <Layout onLogout={logout}><PageWrapper><Dashboard /></PageWrapper></Layout>
        </ProtectedRoute>
      } />
      <Route path="/simulator" element={
        <ProtectedRoute>
          <Layout onLogout={logout}><PageWrapper><Simulator /></PageWrapper></Layout>
        </ProtectedRoute>
      } />
      <Route path="/results" element={
        <ProtectedRoute>
          <Layout onLogout={logout}><PageWrapper><Results /></PageWrapper></Layout>
        </ProtectedRoute>
      } />
      <Route path="/scenarios" element={
        <ProtectedRoute>
          <Layout onLogout={logout}><PageWrapper><Scenarios /></PageWrapper></Layout>
        </ProtectedRoute>
      } />

      {/* ── Catch-all → back to root */}
      <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AnimatePresence>
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
