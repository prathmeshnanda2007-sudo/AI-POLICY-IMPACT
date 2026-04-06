import React from 'react'
import { POLICY_CONFIG } from '../utils/constants'

export default function PolicySlider({ name, value, onChange }) {
  const config = POLICY_CONFIG[name]
  if (!config) return null

  const percentage = ((value - config.min) / (config.max - config.min)) * 100

  return (
    <div className="group p-4 rounded-xl bg-dark-300/50 border border-white/5 hover:border-primary-500/20 transition-all duration-300">
      <div className="flex items-center justify-between mb-1">
        <label className="text-sm font-medium text-gray-200 group-hover:text-white transition-colors">
          {config.label}
        </label>
        <div 
          className="px-3 py-1 rounded-lg text-sm font-bold transition-all duration-300"
          style={{ 
            backgroundColor: `${config.color}15`,
            color: config.color,
            borderColor: `${config.color}30`,
            borderWidth: '1px',
          }}
        >
          {typeof value === 'number' ? value.toFixed(config.step < 1 ? 1 : 0) : value}{config.unit}
        </div>
      </div>
      <p className="text-xs text-gray-500 mb-3">{config.description}</p>
      
      <div className="relative">
        <div className="absolute top-1/2 left-0 h-1.5 rounded-full bg-dark-200 w-full -translate-y-1/2" />
        <div 
          className="absolute top-1/2 left-0 h-1.5 rounded-full -translate-y-1/2 transition-all duration-150"
          style={{ 
            width: `${percentage}%`,
            background: `linear-gradient(90deg, ${config.color}80, ${config.color})`,
          }}
        />
        <input
          type="range"
          min={config.min}
          max={config.max}
          step={config.step}
          value={value}
          onChange={(e) => onChange(name, e.target.value)}
          className="relative z-10 w-full appearance-none bg-transparent cursor-pointer"
          style={{ height: '20px' }}
        />
      </div>
      
      <div className="flex justify-between mt-1">
        <span className="text-[10px] text-gray-600">{config.min}{config.unit}</span>
        <span className="text-[10px] text-gray-600">{config.max}{config.unit}</span>
      </div>
    </div>
  )
}
