import React from 'react'
import {
  LineChart, Line, BarChart, Bar, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  RadialBarChart, RadialBar, PieChart, Pie, Cell,
} from 'recharts'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-dark-300 border border-white/10 rounded-xl p-3 shadow-2xl">
      <p className="text-xs text-gray-400 mb-2">{label}</p>
      {payload.map((entry, i) => (
        <div key={i} className="flex items-center gap-2 text-sm">
          <div className="w-2.5 h-2.5 rounded-full" style={{ background: entry.color }} />
          <span className="text-gray-300">{entry.name}:</span>
          <span className="font-semibold text-white">{typeof entry.value === 'number' ? entry.value.toFixed(2) : entry.value}</span>
        </div>
      ))}
    </div>
  )
}

export function GDPChart({ data }) {
  return (
    <div className="glass-card p-6">
      <h3 className="text-sm font-semibold text-gray-200 mb-4">GDP Growth Prediction</h3>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 11 }} />
          <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Line
            type="monotone"
            dataKey="gdp"
            stroke="#06b6d4"
            strokeWidth={3}
            dot={{ fill: '#06b6d4', r: 4, strokeWidth: 2, stroke: '#0a0f1a' }}
            activeDot={{ r: 6, stroke: '#06b6d4', strokeWidth: 2 }}
            name="GDP Growth %"
          />
          <Line
            type="monotone"
            dataKey="baseline"
            stroke="#334155"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
            name="Baseline"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export function InflationChart({ data }) {
  return (
    <div className="glass-card p-6">
      <h3 className="text-sm font-semibold text-gray-200 mb-4">Inflation Impact</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 11 }} />
          <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Bar dataKey="inflation" fill="#ef4444" radius={[4, 4, 0, 0]} name="Inflation %" />
          <Bar dataKey="baseline" fill="#334155" radius={[4, 4, 0, 0]} name="Baseline" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export function EmploymentChart({ data }) {
  return (
    <div className="glass-card p-6">
      <h3 className="text-sm font-semibold text-gray-200 mb-4">Employment Rate Trend</h3>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 11 }} />
          <YAxis stroke="#64748b" tick={{ fontSize: 11 }} domain={[85, 100]} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <defs>
            <linearGradient id="empGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
            </linearGradient>
          </defs>
          <Area
            type="monotone"
            dataKey="employment"
            stroke="#10b981"
            strokeWidth={3}
            fill="url(#empGrad)"
            name="Employment %"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

export function EnvironmentGauge({ score }) {
  const data = [{ name: 'Score', value: score, fill: '#22c55e' }]
  const bgData = [{ name: 'BG', value: 100, fill: '#1e293b' }]

  return (
    <div className="glass-card p-6">
      <h3 className="text-sm font-semibold text-gray-200 mb-4">Environment Score</h3>
      <div className="flex items-center justify-center">
        <ResponsiveContainer width="100%" height={280}>
          <RadialBarChart
            cx="50%" cy="50%"
            innerRadius="60%" outerRadius="90%"
            barSize={20}
            data={data}
            startAngle={210}
            endAngle={-30}
          >
            <RadialBar
              background={{ fill: '#1e293b' }}
              dataKey="value"
              cornerRadius={10}
            />
            <text
              x="50%" y="45%"
              textAnchor="middle"
              dominantBaseline="middle"
              className="fill-white text-4xl font-bold font-display"
            >
              {score?.toFixed(1) || '—'}
            </text>
            <text
              x="50%" y="58%"
              textAnchor="middle"
              dominantBaseline="middle"
              className="fill-gray-400 text-sm"
            >
              / 100
            </text>
          </RadialBarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export function ComparisonChart({ data, metrics }) {
  const colors = ['#06b6d4', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6']
  return (
    <div className="glass-card p-6">
      <h3 className="text-sm font-semibold text-gray-200 mb-4">Scenario Comparison</h3>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} />
          <YAxis type="category" dataKey="name" stroke="#64748b" tick={{ fontSize: 11 }} width={120} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          {metrics.map((m, i) => (
            <Bar key={m} dataKey={m} fill={colors[i % colors.length]} radius={[0, 4, 4, 0]} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export function FeatureImportanceChart({ data }) {
  const COLORS = ['#06b6d4', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#22c55e']
  return (
    <div className="glass-card p-6">
      <h3 className="text-sm font-semibold text-gray-200 mb-4">Feature Importance (SHAP)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} />
          <YAxis type="category" dataKey="feature" stroke="#64748b" tick={{ fontSize: 11 }} width={160} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="importance" radius={[0, 6, 6, 0]}>
            {data?.map((entry, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
