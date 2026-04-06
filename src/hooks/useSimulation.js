import { useState, useCallback } from 'react'
import { predictPolicy, comparePolicy, saveScenario as saveScenarioApi } from '../services/api'
import { POLICY_DEFAULTS } from '../utils/constants'

export function useSimulation() {
  const [inputs, setInputs] = useState({ ...POLICY_DEFAULTS })
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
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

  const runSimulation = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await predictPolicy(inputs)
      setResults(data)
      setHistory(prev => [
        { id: Date.now(), inputs: { ...inputs }, results: data, timestamp: new Date().toISOString() },
        ...prev.slice(0, 19),
      ])
      return data
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Simulation failed'
      setError(msg)
      return null
    } finally {
      setLoading(false)
    }
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
    error,
    history,
    updateInput,
    resetInputs,
    runSimulation,
    compareScenarios,
    saveCurrentScenario,
  }
}
