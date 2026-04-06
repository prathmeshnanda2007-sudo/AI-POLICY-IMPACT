import React, { useState, useEffect } from 'react'
import { Clock, Trash2, Eye, Download, Filter } from 'lucide-react'
import { getHistory } from '../services/api'
import { OUTPUT_CONFIG, POLICY_CONFIG, formatValue } from '../utils/constants'
import { GDPChart, InflationChart } from '../components/Charts'

export default function Results() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    setLoading(true)
    try {
      const data = await getHistory()
      setHistory(data)
    } catch (err) {
      console.error('Failed to load history:', err)
    } finally {
      setLoading(false)
    }
  }

  const generateChartData = (results) => {
    if (!results) return []
    const baseline = { gdp_growth: 2.5, inflation: 3.0 }
    return Array.from({ length: 6 }, (_, i) => ({
      name: `Y${i + 1}`,
      gdp: parseFloat((baseline.gdp_growth + (results.gdp_growth - baseline.gdp_growth) * (i / 5) + (Math.random() - 0.5) * 0.2).toFixed(2)),
      inflation: parseFloat((baseline.inflation + (results.inflation - baseline.inflation) * (i / 5) + (Math.random() - 0.5) * 0.2).toFixed(2)),
      baseline: parseFloat(baseline.gdp_growth.toFixed(2)),
    }))
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-display font-bold text-white mb-1">Simulation Results</h1>
          <p className="text-sm text-gray-400">History of all past simulations and predictions</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <Clock className="w-3.5 h-3.5" />
          {history.length} simulations recorded
        </div>
      </div>

      <div className="grid lg:grid-cols-12 gap-8">
        {/* History List */}
        <div className="lg:col-span-5 space-y-3">
          {loading ? (
            <div className="glass-card p-12 text-center">
              <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
              <p className="text-sm text-gray-400">Loading history...</p>
            </div>
          ) : history.length === 0 ? (
            <div className="glass-card p-12 text-center">
              <Clock className="w-10 h-10 text-gray-600 mx-auto mb-3" />
              <p className="text-sm text-gray-400">No simulations yet. Run your first simulation!</p>
            </div>
          ) : (
            history.map((item, idx) => (
              <button
                key={item.id || idx}
                onClick={() => setSelected(item)}
                className={`w-full text-left glass-card p-4 transition-all duration-200 hover:border-primary-500/30 ${
                  selected?.id === item.id ? 'border-primary-500/40 bg-primary-500/5' : ''
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-white">
                    {item.name || `Simulation #${history.length - idx}`}
                  </span>
                  <span className="text-[10px] text-gray-500">
                    {item.timestamp ? new Date(item.timestamp).toLocaleDateString() : '—'}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  {['gdp_growth', 'inflation', 'employment_rate'].map((key) => {
                    const config = OUTPUT_CONFIG[key]
                    return (
                      <div key={key} className="text-center">
                        <p className="text-[10px] text-gray-500">{config.label}</p>
                        <p className="text-xs font-bold" style={{ color: config.color }}>
                          {item.results?.[key]?.toFixed(2) || '—'}{config.unit}
                        </p>
                      </div>
                    )
                  })}
                </div>
              </button>
            ))
          )}
        </div>

        {/* Detail Panel */}
        <div className="lg:col-span-7 space-y-6">
          {selected ? (
            <>
              <div className="glass-card p-6">
                <h3 className="text-base font-semibold text-white mb-4">
                  {selected.name || 'Simulation Details'}
                </h3>
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div>
                    <h4 className="text-xs text-gray-400 uppercase tracking-wider mb-3">Inputs</h4>
                    <div className="space-y-2">
                      {Object.entries(selected.inputs || {}).map(([key, val]) => {
                        const config = POLICY_CONFIG[key]
                        return config ? (
                          <div key={key} className="flex justify-between text-sm">
                            <span className="text-gray-400">{config.label}</span>
                            <span className="text-white font-medium">{val}{config.unit}</span>
                          </div>
                        ) : null
                      })}
                    </div>
                  </div>
                  <div>
                    <h4 className="text-xs text-gray-400 uppercase tracking-wider mb-3">Outputs</h4>
                    <div className="space-y-2">
                      {Object.entries(selected.results || {}).map(([key, val]) => {
                        const config = OUTPUT_CONFIG[key]
                        return config ? (
                          <div key={key} className="flex justify-between text-sm">
                            <span className="text-gray-400">{config.label}</span>
                            <span className="font-medium" style={{ color: config.color }}>
                              {typeof val === 'number' ? val.toFixed(2) : val}{config.unit}
                            </span>
                          </div>
                        ) : null
                      })}
                    </div>
                  </div>
                </div>
              </div>

              <GDPChart data={generateChartData(selected.results)} />
              <InflationChart data={generateChartData(selected.results)} />
            </>
          ) : (
            <div className="glass-card p-16 text-center">
              <Eye className="w-10 h-10 text-gray-600 mx-auto mb-3" />
              <p className="text-sm text-gray-400">Select a simulation from the list to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
