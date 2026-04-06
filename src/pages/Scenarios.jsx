import React, { useState, useEffect } from 'react'
import { Plus, Trash2, GitCompare, Lightbulb, BarChart3 } from 'lucide-react'
import PolicySlider from '../components/PolicySlider'
import { ComparisonChart } from '../components/Charts'
import { POLICY_CONFIG, POLICY_DEFAULTS, OUTPUT_CONFIG } from '../utils/constants'
import { getScenarios, deleteScenario, comparePolicy, getRecommendation } from '../services/api'

export default function Scenarios() {
  const [savedScenarios, setSavedScenarios] = useState([])
  const [compareList, setCompareList] = useState([])
  const [comparisonResults, setComparisonResults] = useState(null)
  const [comparing, setComparing] = useState(false)
  const [recommendation, setRecommendation] = useState(null)
  const [loadingRec, setLoadingRec] = useState(false)

  useEffect(() => {
    loadScenarios()
  }, [])

  const loadScenarios = async () => {
    try {
      const data = await getScenarios()
      setSavedScenarios(data)
    } catch (err) {
      console.error('Load scenarios failed:', err)
    }
  }

  const handleDelete = async (id) => {
    try {
      await deleteScenario(id)
      setSavedScenarios(prev => prev.filter(s => s.id !== id))
      setCompareList(prev => prev.filter(s => s.id !== id))
    } catch (err) {
      console.error('Delete failed:', err)
    }
  }

  const toggleCompare = (scenario) => {
    setCompareList(prev => {
      const exists = prev.find(s => s.id === scenario.id)
      if (exists) return prev.filter(s => s.id !== scenario.id)
      if (prev.length >= 4) return prev
      return [...prev, scenario]
    })
  }

  const handleCompare = async () => {
    if (compareList.length < 2) return
    setComparing(true)
    try {
      const scenarios = compareList.map(s => s.inputs)
      const data = await comparePolicy(scenarios)
      const chartData = Object.keys(OUTPUT_CONFIG).map(metric => {
        const row = { name: OUTPUT_CONFIG[metric].label }
        data.forEach((result, i) => {
          row[compareList[i].name || `Scenario ${i + 1}`] = result[metric]
        })
        return row
      })
      setComparisonResults({
        data: chartData,
        metrics: compareList.map(s => s.name || `Scenario`),
        raw: data,
      })
    } catch (err) {
      console.error('Comparison failed:', err)
    } finally {
      setComparing(false)
    }
  }

  const handleRecommendation = async () => {
    setLoadingRec(true)
    try {
      const target = { gdp_growth: 4.0, inflation: 2.5, employment_rate: 96, environment_score: 80 }
      const data = await getRecommendation(target)
      setRecommendation(data)
    } catch (err) {
      console.error('Recommendation failed:', err)
    } finally {
      setLoadingRec(false)
    }
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-display font-bold text-white mb-1">Scenario Comparison</h1>
          <p className="text-sm text-gray-400">Compare saved scenarios and get AI-powered recommendations</p>
        </div>
        <button
          onClick={handleRecommendation}
          disabled={loadingRec}
          className="btn-secondary flex items-center gap-2 text-sm"
        >
          <Lightbulb className="w-4 h-4" />
          {loadingRec ? 'Thinking...' : 'AI Recommendation'}
        </button>
      </div>

      {/* AI Recommendation */}
      {recommendation && (
        <div className="glass-card p-6 border-primary-500/20 glow-border">
          <div className="flex items-center gap-2 mb-4">
            <Lightbulb className="w-5 h-5 text-primary-400" />
            <h3 className="text-sm font-semibold text-white">AI Policy Recommendation</h3>
          </div>
          <p className="text-sm text-gray-300 mb-4">
            Based on multi-objective optimization, we recommend these policy settings for balanced growth:
          </p>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {Object.entries(recommendation.recommended_inputs || {}).map(([key, val]) => {
              const config = POLICY_CONFIG[key]
              return config ? (
                <div key={key} className="p-3 rounded-xl bg-dark-300/50 border border-white/5">
                  <p className="text-xs text-gray-400">{config.label}</p>
                  <p className="text-lg font-bold text-primary-400">
                    {typeof val === 'number' ? val.toFixed(1) : val}{config.unit}
                  </p>
                </div>
              ) : null
            })}
          </div>
          {recommendation.predicted_outcomes && (
            <div className="mt-4 pt-4 border-t border-white/5">
              <p className="text-xs text-gray-400 mb-3">Expected Outcomes:</p>
              <div className="grid grid-cols-5 gap-3">
                {Object.entries(recommendation.predicted_outcomes).map(([key, val]) => {
                  const config = OUTPUT_CONFIG[key]
                  return config ? (
                    <div key={key} className="text-center">
                      <p className="text-[10px] text-gray-500">{config.label}</p>
                      <p className="text-sm font-bold" style={{ color: config.color }}>
                        {typeof val === 'number' ? val.toFixed(2) : val}
                      </p>
                    </div>
                  ) : null
                })}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="grid lg:grid-cols-12 gap-8">
        {/* Scenarios List */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-200">Saved Scenarios ({savedScenarios.length})</h3>
            {compareList.length >= 2 && (
              <button
                onClick={handleCompare}
                disabled={comparing}
                className="btn-primary text-xs px-4 py-2 flex items-center gap-1"
              >
                <GitCompare className="w-3.5 h-3.5" />
                {comparing ? 'Comparing...' : `Compare (${compareList.length})`}
              </button>
            )}
          </div>

          {savedScenarios.length === 0 ? (
            <div className="glass-card p-12 text-center">
              <BarChart3 className="w-10 h-10 text-gray-600 mx-auto mb-3" />
              <p className="text-sm text-gray-400">No saved scenarios. Run a simulation and save it!</p>
            </div>
          ) : (
            savedScenarios.map((scenario) => {
              const isSelected = compareList.find(s => s.id === scenario.id)
              return (
                <div
                  key={scenario.id}
                  className={`glass-card p-4 transition-all duration-200 ${
                    isSelected ? 'border-primary-500/40 bg-primary-500/5' : ''
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-semibold text-white">{scenario.name}</span>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => toggleCompare(scenario)}
                        className={`p-1.5 rounded-lg transition-colors text-xs ${
                          isSelected
                            ? 'bg-primary-500/20 text-primary-400'
                            : 'hover:bg-white/5 text-gray-500'
                        }`}
                      >
                        <GitCompare className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleDelete(scenario.id)}
                        className="p-1.5 rounded-lg hover:bg-red-500/10 text-gray-500 hover:text-red-400 transition-colors"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    {['gdp_growth', 'inflation', 'environment_score'].map((key) => {
                      const config = OUTPUT_CONFIG[key]
                      return (
                        <div key={key} className="text-center">
                          <p className="text-[10px] text-gray-500">{config.label}</p>
                          <p className="text-xs font-bold" style={{ color: config.color }}>
                            {scenario.results?.[key]?.toFixed(2) || '—'}
                          </p>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )
            })
          )}
        </div>

        {/* Comparison Results */}
        <div className="lg:col-span-7">
          {comparisonResults ? (
            <ComparisonChart
              data={comparisonResults.data}
              metrics={comparisonResults.metrics}
            />
          ) : (
            <div className="glass-card p-16 text-center">
              <GitCompare className="w-10 h-10 text-gray-600 mx-auto mb-3" />
              <h3 className="text-base font-semibold text-white mb-2">Compare Scenarios</h3>
              <p className="text-sm text-gray-400 max-w-sm mx-auto">
                Select 2-4 saved scenarios from the list and click "Compare" to see side-by-side analysis.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
