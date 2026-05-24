import { useState, useCallback } from 'react'
import { predictPolicy, comparePolicy, saveScenario as saveScenarioApi } from '../services/api'
import { POLICY_DEFAULTS } from '../utils/constants'

export function useSimulation() {
  const [inputs, setInputs] = useState({ ...POLICY_DEFAULTS })
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [progressStep, setProgressStep] = useState(null)
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])

  const updateInput = useCallback((key, value) => {
    setInputs(prev => ({ ...prev, [key]: parseFloat(value) }))
  }, [])

  const resetInputs = useCallback(() => {
    setInputs({ ...POLICY_DEFAULTS })
    setResults(null)
    setError(null)
  }, [])

  const runSimulation = useCallback(() => {
    return new Promise((resolve) => {
      setLoading(true)
      setError(null)
      setProgressStep('Connecting to AI Engine...')
      
      const wsUrl = import.meta.env.VITE_API_URL 
        ? import.meta.env.VITE_API_URL.replace('http', 'ws') + '/ws/simulate'
        : 'ws://localhost:8000/ws/simulate'
        
      const ws = new WebSocket(wsUrl)
      
      ws.onopen = () => {
        ws.send(JSON.stringify(inputs))
      }
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.status === 'processing') {
            setProgressStep(data.step)
          } else if (data.status === 'complete') {
            setResults(data.results)
            setHistory(prev => [
              { id: Date.now(), inputs: { ...inputs }, results: data.results, timestamp: new Date().toISOString() },
              ...prev.slice(0, 19),
            ])
            ws.close()
            setLoading(false)
            setProgressStep(null)
            resolve(data.results)
          } else if (data.status === 'error') {
            setError(data.message)
            ws.close()
            setLoading(false)
            setProgressStep(null)
            resolve(null)
          }
        } catch (e) {
          console.error("WS parsing error", e)
        }
      }
      
      ws.onerror = () => {
        setError("Connection to AI Engine lost.")
        setLoading(false)
        setProgressStep(null)
        resolve(null)
      }
    })
  }, [inputs])

  const compareScenarios = useCallback(async (scenarios) => {
    setLoading(true)
    setError(null)
    try {
      const data = await comparePolicy(scenarios)
      return data
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Comparison failed'
      setError(msg)
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  const saveCurrentScenario = useCallback(async (name) => {
    if (!results) return null
    try {
      const scenario = {
        name,
        inputs: { ...inputs },
        results,
      }
      const saved = await saveScenarioApi(scenario)
      return saved
    } catch (err) {
      setError(err.message)
      return null
    }
  }, [inputs, results])

  return {
    inputs,
    results,
    loading,
    progressStep,
    error,
    history,
    updateInput,
    resetInputs,
    runSimulation,
    compareScenarios,
    saveCurrentScenario,
  }
}
