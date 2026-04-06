import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

// Attach token from localStorage on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('policyai_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 responses globally — redirect to login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('policyai_token')
      // Only redirect if not already on auth pages
      if (!window.location.pathname.startsWith('/login') && 
          !window.location.pathname.startsWith('/signup') &&
          window.location.pathname !== '/') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// --- Auth API ---

export async function authRegister(email, password, name) {
  const res = await api.post('/auth/register', { email, password, name })
  return res.data
}

export async function authLogin(email, password) {
  const res = await api.post('/auth/login', { email, password })
  return res.data
}

export async function authVerify() {
  const res = await api.post('/auth/verify')
  return res.data
}

export async function authMe() {
  const res = await api.get('/auth/me')
  return res.data
}

// --- Policy API ---

export async function predictPolicy(inputs) {
  const res = await api.post('/predict', inputs)
  return res.data
}

export async function comparePolicy(scenarios) {
  const res = await api.post('/compare', { scenarios })
  return res.data
}

export async function trainModel() {
  const res = await api.post('/train')
  return res.data
}

export async function getScenarios() {
  const res = await api.get('/scenarios')
  return res.data
}

export async function saveScenario(scenario) {
  const res = await api.post('/scenarios', scenario)
  return res.data
}

export async function deleteScenario(id) {
  const res = await api.delete(`/scenarios/${id}`)
  return res.data
}

export async function getHistory() {
  const res = await api.get('/history')
  return res.data
}

export async function getModelInfo() {
  const res = await api.get('/model/info')
  return res.data
}

export async function getFeatureImportance() {
  const res = await api.get('/model/feature-importance')
  return res.data
}

export async function getSensitivity(params) {
  const res = await api.post('/sensitivity', params)
  return res.data
}

export async function getRecommendation(target) {
  const res = await api.post('/recommend', target)
  return res.data
}

export default api
