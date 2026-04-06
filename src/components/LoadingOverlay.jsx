import React from 'react'
import { Brain, Loader2 } from 'lucide-react'

export default function LoadingOverlay({ message = 'Running ML Model...' }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-dark-500/80 backdrop-blur-sm">
      <div className="glass-card p-10 flex flex-col items-center gap-5 animate-fade-in">
        <div className="relative">
          <div className="w-20 h-20 rounded-full border-4 border-primary-500/20 flex items-center justify-center">
            <Brain className="w-8 h-8 text-primary-400" />
          </div>
          <Loader2 className="absolute -top-1 -left-1 w-[88px] h-[88px] text-primary-500 animate-spin" style={{ animationDuration: '2s' }} />
        </div>
        <div className="text-center">
          <p className="text-lg font-semibold text-white mb-1">{message}</p>
          <p className="text-sm text-gray-400">Analyzing policy parameters with Random Forest model</p>
        </div>
        <div className="flex gap-1.5">
          {[0, 1, 2].map(i => (
            <div
              key={i}
              className="w-2.5 h-2.5 rounded-full bg-primary-500"
              style={{
                animation: 'pulse 1.4s ease-in-out infinite',
                animationDelay: `${i * 0.2}s`,
              }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
