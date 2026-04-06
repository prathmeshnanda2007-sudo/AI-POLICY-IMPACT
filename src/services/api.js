import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

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
