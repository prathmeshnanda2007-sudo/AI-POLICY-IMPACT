import React, { useEffect } from 'react'
import { BarChart3, TrendingUp, Globe, Shield, Zap, Target } from 'lucide-react'
import ShaderShowcase from '@/components/ui/hero'
import Lenis from '@studio-freight/lenis'
import { ZoomParallax } from '@/components/ui/zoom-parallax'

// Feature card component
function FeatureCard({ icon: Icon, title, description, colorClass }) {
  return (
    <div className="p-8 rounded-3xl bg-white border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
      <div className={`w-14 h-14 rounded-2xl ${colorClass} flex items-center justify-center mb-6`}>
        <Icon className="w-7 h-7 text-white" />
      </div>
      <h3 className="text-xl font-bold text-slate-900 mb-3">{title}</h3>
      <p className="text-slate-600 leading-relaxed">{description}</p>
    </div>
  )
}

export default function Landing() {
  useEffect(() => {
    const lenis = new Lenis()
   
    function raf(time) {
      lenis.raf(time)
      requestAnimationFrame(raf)
    }

    requestAnimationFrame(raf)
  }, [])

  const parallaxImages = [
    {
      src: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=1280&auto=format&fit=crop',
      alt: 'Modern institutional architecture',
    },
    {
      src: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1280&auto=format&fit=crop',
      alt: 'Global network and connectivity',
    },
    {
      src: 'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?q=80&w=1280&auto=format&fit=crop',
      alt: 'Smart city infrastructure',
    },
    {
      src: 'https://images.unsplash.com/photo-1466611653911-95081537e5b7?q=80&w=1280&auto=format&fit=crop',
      alt: 'Sustainable wind energy',
    },
    {
      src: 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?q=80&w=1280&auto=format&fit=crop',
      alt: 'AI neural network simulation',
    },
    {
      src: 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?q=80&w=1280&auto=format&fit=crop',
      alt: 'Data server processing',
    },
    {
      src: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=1280&auto=format&fit=crop',
      alt: 'Digital cyber infrastructure',
    },
  ]

  return (
    <div className="w-full bg-slate-50 min-h-screen">
      {/* Hero Section */}
      <ShaderShowcase />

      {/* Zoom Parallax Section */}
      <section className="bg-slate-50 relative">
        <div className="relative flex h-[30vh] items-center justify-center">
          <div
            aria-hidden="true"
            className="pointer-events-none absolute -top-1/2 left-1/2 h-[120vmin] w-[120vmin] -translate-x-1/2 rounded-full bg-[radial-gradient(ellipse_at_center,rgba(6,182,212,0.1),transparent_50%)] blur-[30px]"
          />
          <h2 className="text-center text-3xl font-bold text-slate-900 tracking-tight">
            See the Big Picture
          </h2>
        </div>
        <ZoomParallax images={parallaxImages} />
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-6 md:px-16 bg-white border-t border-slate-100">
        <div className="max-w-6xl mx-auto">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-sm font-bold text-cyan-600 tracking-widest uppercase mb-3">Comprehensive Analysis</h2>
            <h3 className="text-4xl md:text-5xl font-extrabold text-slate-900 tracking-tight mb-6">
              Everything you need to evaluate policy impact.
            </h3>
            <p className="text-lg text-slate-600 leading-relaxed">
              Nexora uses advanced machine learning models trained on historical economic data to accurately simulate how changes in one sector cascade through the entire economy.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard 
              icon={TrendingUp}
              title="GDP Growth Prediction"
              description="Instantly forecast how changes in tax rates and public spending will affect national gross domestic product over time."
              colorClass="bg-blue-500 shadow-blue-500/30"
            />
            <FeatureCard 
              icon={Target}
              title="Inflation Tracking"
              description="Understand the delicate balance between economic stimulus and inflation. See how subsidies and interest rates move prices."
              colorClass="bg-orange-500 shadow-orange-500/30"
            />
            <FeatureCard 
              icon={Globe}
              title="Environmental Scoring"
              description="Calculate the exact ecological impact of industrial deregulation vs strict environmental policies."
              colorClass="bg-emerald-500 shadow-emerald-500/30"
            />
            <FeatureCard 
              icon={BarChart3}
              title="Employment Rates"
              description="Simulate job market reactions to fuel prices, interest rates, and government public spending initiatives."
              colorClass="bg-cyan-500 shadow-cyan-500/30"
            />
            <FeatureCard 
              icon={Shield}
              title="Public Confidence"
              description="Gauge public satisfaction and market confidence metrics derived from the aggregate effects of your policy choices."
              colorClass="bg-violet-500 shadow-violet-500/30"
            />
            <FeatureCard 
              icon={Zap}
              title="Real-time Scenarios"
              description="Save, load, and compare different legislative scenarios side-by-side to find the optimal path forward."
              colorClass="bg-amber-500 shadow-amber-500/30"
            />
          </div>
        </div>
      </section>

      {/* How it Works Section */}
      <section id="how-it-works" className="py-24 px-6 md:px-16 bg-slate-50">
        <div className="max-w-6xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-extrabold text-slate-900 mb-8">Ready to shape the future?</h2>
          <p className="text-xl text-slate-600 mb-10 max-w-2xl mx-auto">
            Join thousands of policy makers, economists, and researchers using AI to build a better tomorrow.
          </p>
          <a href="/signup" className="inline-block px-10 py-4 rounded-full bg-slate-900 text-white font-semibold text-lg transition-all shadow-lg hover:bg-slate-800 hover:-translate-y-1">
            Create Free Account
          </a>
        </div>
      </section>

      {/* Simple Footer */}
      <footer className="bg-white py-10 border-t border-slate-200">
        <div className="max-w-6xl mx-auto px-6 text-center text-slate-500 text-sm">
          <p>&copy; 2026 Nexora. Simulated impacts are predictions based on ML models.</p>
        </div>
      </footer>
    </div>
  )
}
