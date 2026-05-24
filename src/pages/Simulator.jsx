import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Cpu, RotateCcw, Save, AlertTriangle, CheckCircle, XCircle, Download, FileText } from 'lucide-react'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import PolicySlider from '../components/PolicySlider'
import ResultCard from '../components/ResultCard'
import LoadingOverlay from '../components/LoadingOverlay'
import { GDPChart, InflationChart, EmploymentChart, EnvironmentGauge, FeatureImportanceChart } from '../components/Charts'
import { useSimulation } from '../hooks/useSimulation'
import { POLICY_CONFIG, OUTPUT_CONFIG, getRiskLevel } from '../utils/constants'
import { getFeatureImportance, getSensitivity } from '../services/api'

export default function Simulator() {
  const {
    inputs, results, loading, progressStep, error,
    updateInput, resetInputs, runSimulation, saveCurrentScenario,
  } = useSimulation()

  const [saveName, setSaveName] = useState('')
  const [showSave, setShowSave] = useState(false)
  const [saveStatus, setSaveStatus] = useState(null)
  const [featureImportance, setFeatureImportance] = useState(null)
  const [sensitivity, setSensitivity] = useState(null)

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  }

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" } }
  }

  const handleRun = async () => {
    const data = await runSimulation()
    if (data) {
      // Load feature importance after successful prediction
      try {
        const fi = await getFeatureImportance()
        setFeatureImportance(fi)
      } catch (e) {
        console.log('Feature importance not available')
      }
    }
  }

  const handleSave = async () => {
    if (!saveName.trim()) return
    setSaveStatus('saving')
    const saved = await saveCurrentScenario(saveName)
    if (saved) {
      setSaveStatus('success')
      setTimeout(() => { setShowSave(false); setSaveStatus(null); setSaveName('') }, 1500)
    } else {
      setSaveStatus('error')
    }
  }

  const handleDownload = () => {
    if (!results) return
    const exportData = {
      scenario: saveName || "Unsaved Scenario",
      timestamp: new Date().toISOString(),
      inputs,
      results
    }
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `simulation-results-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleDownloadPDF = async () => {
    const el = document.getElementById('results-panel-export')
    if (!el) return
    try {
      const canvas = await html2canvas(el, {
        scale: 2,
        useCORS: true,
        backgroundColor: '#070b14'
      })
      const imgData = canvas.toDataURL('image/png')
      const pdf = new jsPDF({
        orientation: 'p',
        unit: 'px',
        format: [canvas.width / 2, canvas.height / 2]
      })
      pdf.addImage(imgData, 'PNG', 0, 0, canvas.width / 2, canvas.height / 2)
      pdf.save(`simulation-results-${Date.now()}.pdf`)
    } catch (err) {
      console.error('Failed to export PDF:', err)
    }
  }

  const risk = results ? getRiskLevel(results) : null

  // Generate chart projection data from results
  const generateChartData = (metric, value) => {
    const baseline = { gdp_growth: 2.5, inflation: 3.0, employment_rate: 94, environment_score: 55 }
    const bv = baseline[metric] || 0
    return Array.from({ length: 6 }, (_, i) => {
      const t = i / 5
      const projected = bv + (value - bv) * t + (Math.random() - 0.5) * 0.3
      return {
        name: `Y${i + 1}`,
        [metric === 'gdp_growth' ? 'gdp' : metric === 'inflation' ? 'inflation' : 'employment']: parseFloat(projected.toFixed(2)),
        baseline: parseFloat(bv.toFixed(2)),
      }
    })
  }

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6 lg:space-y-0 lg:grid lg:grid-cols-12 lg:gap-8">
      {loading && <LoadingOverlay progressStep={progressStep} />}

      <motion.div variants={item} className="lg:col-span-5 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-white mb-1">Policy Simulator</h1>
            <p className="text-sm text-gray-400">Adjust policy parameters and predict economic impact</p>
          </div>
          {results && risk && (
            <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${
              risk.color === 'red' ? 'bg-red-500/10 border border-red-500/20' :
              risk.color === 'yellow' ? 'bg-amber-500/10 border border-amber-500/20' :
              'bg-emerald-500/10 border border-emerald-500/20'
            }`}>
              {risk.color === 'red' ? <AlertTriangle className="w-4 h-4 text-red-400" /> :
               risk.color === 'yellow' ? <AlertTriangle className="w-4 h-4 text-amber-400" /> :
               <CheckCircle className="w-4 h-4 text-emerald-400" />}
              <span className={`text-xs font-bold ${
                risk.color === 'red' ? 'text-red-400' :
                risk.color === 'yellow' ? 'text-amber-400' :
                'text-emerald-400'
              }`}>{risk.level}</span>
            </div>
          )}
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-base font-semibold text-white">Policy Parameters</h2>
              <p className="text-xs text-gray-500 mt-1">Adjust the sliders to configure your policy scenario</p>
            </div>
            <button onClick={resetInputs} className="p-2 rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition-colors" title="Reset to defaults">
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
          <div className="space-y-4">
            {Object.keys(POLICY_CONFIG).map((key) => (
              <PolicySlider
                key={key}
                name={key}
                value={inputs[key]}
                onChange={updateInput}
              />
            ))}
          </div>
          <div className="mt-6 flex gap-3">
            <button onClick={handleRun} disabled={loading} className="btn-primary flex-1 flex items-center justify-center gap-2">
              <Cpu className="w-4 h-4" />
              Run Simulation
            </button>
            {results && (
              <>
                <button onClick={() => setShowSave(!showSave)} className="btn-secondary px-4" title="Save Scenario">
                  <Save className="w-4 h-4" />
                </button>
                <button onClick={handleDownload} className="btn-secondary px-4" title="Download JSON">
                  <Download className="w-4 h-4" />
                </button>
                <button onClick={handleDownloadPDF} className="btn-secondary px-4" title="Download PDF Report">
                  <FileText className="w-4 h-4" />
                </button>
              </>
            )}
          </div>

          {showSave && (
            <div className="mt-4 p-4 rounded-xl bg-dark-200 border border-white/10 animate-slide-up">
              <label className="text-xs text-gray-400 mb-2 block">Scenario Name</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={saveName}
                  onChange={(e) => setSaveName(e.target.value)}
                  placeholder="e.g. High tax + Green policy"
                  className="input-dark text-sm flex-1"
                />
                <button onClick={handleSave} className="btn-primary text-sm px-4">
                  {saveStatus === 'saving' ? 'Saving...' : saveStatus === 'success' ? '✓ Saved!' : 'Save'}
                </button>
              </div>
            </div>
          )}

          {error && (
            <div className="mt-4 p-4 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center gap-3">
              <XCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}
        </div>
      </motion.div>

      <motion.div variants={item} className="lg:col-span-7 space-y-6" id="results-panel-export">
        {results ? (
          <>
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.keys(OUTPUT_CONFIG).map((key) => (
                <ResultCard key={key} metric={key} value={results[key]} />
              ))}
            </div>

            <div className="grid lg:grid-cols-2 gap-6">
              <GDPChart data={generateChartData('gdp_growth', results.gdp_growth)} />
              <InflationChart data={generateChartData('inflation', results.inflation)} />
            </div>
            <div className="grid lg:grid-cols-2 gap-6">
              <EmploymentChart data={generateChartData('employment_rate', results.employment_rate)} />
              <EnvironmentGauge score={results.environment_score} />
            </div>

            {featureImportance && featureImportance.length > 0 && (
              <FeatureImportanceChart data={featureImportance} />
            )}

            {results.confidence && (
              <div className="glass-card p-6">
                <h3 className="text-sm font-semibold text-gray-200 mb-3">Prediction Confidence</h3>
                <div className="flex items-center gap-4">
                  <div className="flex-1 bg-dark-200 rounded-full h-3 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-primary-500 to-emerald-500 transition-all duration-1000"
                      style={{ width: `${results.confidence * 100}%` }}
                    />
                  </div>
                  <span className="text-lg font-bold text-primary-400">
                    {(results.confidence * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="glass-card p-16 flex flex-col items-center justify-center text-center">
            <div className="w-20 h-20 rounded-full bg-primary-500/10 flex items-center justify-center mb-6">
              <Cpu className="w-8 h-8 text-primary-400" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Ready to Simulate</h3>
            <p className="text-sm text-gray-400 max-w-sm">
              Adjust the policy parameters on the left and click "Run Simulation" to see AI-predicted outcomes.
            </p>
          </div>
        )}
      </motion.div>
    </motion.div>
  )
}
