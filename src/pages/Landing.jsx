import React from 'react'
import { Link } from 'react-router-dom'
import { Brain, ArrowRight, BarChart3, Cpu, Shield, Globe, Zap, ChevronRight } from 'lucide-react'
import ShaderAnimation from '@/components/ui/spiral-shader'

export default function Landing() {
  return (
    <div className="min-h-screen bg-dark-500 overflow-hidden">
      {/* Animated Spiral Shader Background */}
      <div className="fixed inset-0 opacity-40">
        <ShaderAnimation />
      </div>
      <div className="fixed inset-0 bg-gradient-to-b from-dark-500/30 via-transparent to-dark-500/90" />

      {/* Navigation */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-5 max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <span className="font-display font-bold text-xl text-white">PolicyAI</span>
        </div>
        <div className="hidden md:flex items-center gap-8 text-sm text-gray-400">
          <a href="#features" className="hover:text-white transition-colors">How It Works</a>
          <a href="#features" className="hover:text-white transition-colors">Features</a>
          <a href="#stats" className="hover:text-white transition-colors">Benefits</a>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login" className="text-sm text-gray-400 hover:text-white transition-colors px-4 py-2">
            Sign In
          </Link>
          <Link to="/signup" className="btn-primary text-sm px-5 py-2.5">
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 max-w-7xl mx-auto px-8 pt-20 pb-32 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-500/10 border border-primary-500/20 mb-8">
          <Zap className="w-3.5 h-3.5 text-primary-400" />
          <span className="text-xs font-medium text-primary-400">AI-Powered Policy Simulation Engine</span>
        </div>

        <h1 className="font-display text-5xl md:text-7xl font-bold mb-6 leading-tight">
          <span className="gradient-text">Simulate Policy.</span>
          <br />
          <span className="text-white">Predict Reality.</span>
        </h1>

        <p className="text-lg text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          Test tax rates, subsidies, fuel pricing, and environmental regulations before implementation.
          Our ML engine predicts economic and environmental impacts with{' '}
          <span className="text-primary-400 font-semibold">94% accuracy</span>.
        </p>

        <div className="flex items-center justify-center gap-4 mb-16">
          <Link to="/signup" className="btn-primary text-base px-8 py-4 flex items-center gap-2">
            Start Simulating Free <ArrowRight className="w-4 h-4" />
          </Link>
          <Link to="/login" className="btn-secondary text-base px-8 py-4 flex items-center gap-2">
            Sign In <ChevronRight className="w-4 h-4" />
          </Link>
        </div>

        {/* Preview Card */}
        <div className="max-w-3xl mx-auto glass-card p-1">
          <div className="bg-dark-300 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm text-gray-400">Live Simulation Preview</span>
              <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-xs text-emerald-400 font-medium">Running</span>
              </div>
            </div>
            <div className="grid grid-cols-4 gap-4 mb-4">
              {[
                { label: 'Tax Rate', value: '+18%', color: '#06b6d4' },
                { label: 'Carbon Tax', value: '$45/ton', color: '#f59e0b' },
                { label: 'EV Subsidy', value: '+25%', color: '#10b981' },
                { label: 'Transport Sub.', value: '+15%', color: '#8b5cf6' },
              ].map((item) => (
                <div key={item.label} className="text-center">
                  <p className="text-xs text-gray-500 mb-1">{item.label}</p>
                  <p className="text-base font-bold" style={{ color: item.color }}>{item.value}</p>
                </div>
              ))}
            </div>
            <div className="border-t border-white/5 pt-4 grid grid-cols-3 gap-4">
              {[
                { label: 'GDP Δ', value: '+0.6%', color: '#10b981' },
                { label: 'Inflation Δ', value: '+1.8%', color: '#ef4444' },
                { label: 'Emissions Δ', value: '-12.4%', color: '#22c55e' },
              ].map((item) => (
                <div key={item.label} className="text-center">
                  <p className="text-xs text-gray-500 mb-1">{item.label}</p>
                  <p className="text-lg font-bold" style={{ color: item.color }}>{item.value}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section id="stats" className="relative z-10 max-w-7xl mx-auto px-8 py-16">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {[
            { value: '47+', label: 'Economic Indicators' },
            { value: '12', label: 'Policy Variables' },
            { value: '94%', label: 'Prediction Accuracy' },
            { value: '180+', label: 'Countries Covered' },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <p className="text-4xl font-display font-bold gradient-text mb-2">{stat.value}</p>
              <p className="text-sm text-gray-400">{stat.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section id="features" className="relative z-10 max-w-7xl mx-auto px-8 py-24">
        <h2 className="text-3xl font-display font-bold text-center mb-16">
          <span className="text-white">Powered by </span>
          <span className="gradient-text">Machine Learning</span>
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              icon: Cpu,
              title: 'Random Forest ML',
              desc: 'Advanced ensemble model trained on 5,000+ synthetic policy scenarios with cross-validated accuracy.',
            },
            {
              icon: BarChart3,
              title: 'Real-time Predictions',
              desc: 'Instant GDP, inflation, employment, and environmental impact predictions as you adjust policy parameters.',
            },
            {
              icon: Shield,
              title: 'Risk Assessment',
              desc: 'Automatic risk level evaluation identifies high-risk policies before implementation.',
            },
            {
              icon: Globe,
              title: 'Scenario Comparison',
              desc: 'Compare multiple policy scenarios side-by-side to find the optimal policy configuration.',
            },
            {
              icon: Zap,
              title: 'Sensitivity Analysis',
              desc: 'Understand which policy variables have the greatest impact on each economic indicator.',
            },
            {
              icon: Brain,
              title: 'Policy Recommendations',
              desc: 'AI-powered recommendations suggest optimal policy adjustments for your desired outcomes.',
            },
          ].map(({ icon: Icon, title, desc }) => (
            <div key={title} className="glass-card-hover p-8 group">
              <div className="w-12 h-12 rounded-xl bg-primary-500/10 flex items-center justify-center mb-4 group-hover:bg-primary-500/20 transition-colors">
                <Icon className="w-6 h-6 text-primary-400" />
              </div>
              <h3 className="font-display font-semibold text-lg text-white mb-2">{title}</h3>
              <p className="text-sm text-gray-400 leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="relative z-10 max-w-4xl mx-auto px-8 py-24 text-center">
        <h2 className="text-4xl font-display font-bold mb-4">
          <span className="text-white">Ready to Test Your</span>
          <br />
          <span className="gradient-text">Policy Ideas?</span>
        </h2>
        <p className="text-gray-400 mb-8">
          Join thousands of policymakers and economists using AI to design better public policies.
        </p>
        <Link to="/signup" className="btn-primary text-base px-10 py-4 inline-flex items-center gap-2 mx-auto">
          Create Free Account <ArrowRight className="w-4 h-4" />
        </Link>
        <p className="text-xs text-gray-500 mt-4">Free to use. No credit card required.</p>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/5 py-8 text-center text-xs text-gray-500">
        © 2026 PolicyAI. AI Public Policy Impact Simulator.
      </footer>
    </div>
  )
}
