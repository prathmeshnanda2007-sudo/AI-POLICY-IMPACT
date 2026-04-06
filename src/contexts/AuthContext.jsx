import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(() => localStorage.getItem('policyai_token'))
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Set/remove auth header whenever token changes
  useEffect(() => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      localStorage.setItem('policyai_token', token)
    } else {
      delete api.defaults.headers.common['Authorization']
      localStorage.removeItem('policyai_token')
    }
  }, [token])

  // Verify token on mount
  useEffect(() => {
    const verifyAuth = async () => {
      if (!token) {
        setLoading(false)
        return
      }
      try {
        const res = await api.post('/auth/verify')
        setUser(res.data.user)
      } catch (err) {
        // Token invalid — clear it
        setToken(null)
        setUser(null)
      } finally {
        setLoading(false)
      }
    }
    verifyAuth()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const register = useCallback(async (email, password, name) => {
    setError(null)
    try {
      const res = await api.post('/auth/register', { email, password, name })
      setToken(res.data.token)
      setUser(res.data.user)
      return res.data
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Registration failed'
      setError(msg)
      throw new Error(msg)
    }
  }, [])

  const login = useCallback(async (email, password) => {
    setError(null)
    try {
      const res = await api.post('/auth/login', { email, password })
      setToken(res.data.token)
      setUser(res.data.user)
      return res.data
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Login failed'
      setError(msg)
      throw new Error(msg)
    }
  }, [])

  const logout = useCallback(() => {
    setToken(null)
    setUser(null)
    setError(null)
    localStorage.removeItem('policyai_token')
    delete api.defaults.headers.common['Authorization']
  }, [])

  const isAuthenticated = !!user && !!token

  const value = {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    register,
    login,
    logout,
    setError,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export default AuthContext
