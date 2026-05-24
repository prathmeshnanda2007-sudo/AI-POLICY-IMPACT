"use client"
import { useEffect, useRef, useState } from "react"
import { MeshGradient, PulsingBorder } from "@paper-design/shaders-react"
import { motion } from "framer-motion"
import { useNavigate } from "react-router-dom"
import { Brain } from "lucide-react"

export default function ShaderShowcase() {
  const containerRef = useRef<HTMLDivElement>(null)
  const [isActive, setIsActive] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    const handleMouseEnter = () => setIsActive(true)
    const handleMouseLeave = () => setIsActive(false)

    const container = containerRef.current
    if (container) {
      container.addEventListener("mouseenter", handleMouseEnter)
      container.addEventListener("mouseleave", handleMouseLeave)
    }

    return () => {
      if (container) {
        container.removeEventListener("mouseenter", handleMouseEnter)
        container.removeEventListener("mouseleave", handleMouseLeave)
      }
    }
  }, [])

  return (
    <div ref={containerRef} className="min-h-[90vh] bg-slate-50 relative overflow-hidden flex flex-col">
      <svg className="absolute inset-0 w-0 h-0">
        <defs>
          <filter id="glass-effect" x="-50%" y="-50%" width="200%" height="200%">
            <feTurbulence baseFrequency="0.005" numOctaves="1" result="noise" />
            <feDisplacementMap in="SourceGraphic" in2="noise" scale="0.3" />
            <feColorMatrix
              type="matrix"
              values="1 0 0 0 0.02
                      0 1 0 0 0.02
                      0 0 1 0 0.05
                      0 0 0 0.9 0"
              result="tint"
            />
          </filter>
          <filter id="gooey-filter" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur" />
            <feColorMatrix
              in="blur"
              mode="matrix"
              values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 19 -9"
              result="gooey"
            />
            <feComposite in="SourceGraphic" in2="gooey" operator="atop" />
          </filter>
          <filter id="logo-glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <linearGradient id="logo-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#06b6d4" />
            <stop offset="50%" stopColor="#0ea5e9" />
            <stop offset="100%" stopColor="#2563eb" />
          </linearGradient>
          <filter id="text-glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
      </svg>

      {/* Light Theme Mesh Gradient */}
      <MeshGradient
        className="absolute inset-0 w-full h-full"
        colors={["#ffffff", "#e0f2fe", "#bae6fd", "#7dd3fc", "#f0f9ff"]}
        speed={0.2}
        backgroundColor="#f8fafc"
      />
      <MeshGradient
        className="absolute inset-0 w-full h-full opacity-40"
        colors={["#ffffff", "#f8fafc", "#bae6fd", "#e0f2fe"]}
        speed={0.15}
        wireframe={true}
        backgroundColor="transparent"
      />

      <header className="relative z-20 flex items-center justify-between p-6 md:px-12">
        <motion.div
          className="flex items-center gap-3 group cursor-pointer"
          whileHover={{ scale: 1.05 }}
          transition={{ type: "spring", stiffness: 400, damping: 10 }}
          onClick={() => navigate('/')}
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <span className="font-display font-bold text-xl text-slate-800 tracking-tight">Nexora</span>
        </motion.div>

        {/* Navigation */}
        <nav className="hidden md:flex items-center space-x-2">
          <a
            href="#features"
            className="text-slate-600 hover:text-slate-900 text-sm font-medium px-4 py-2 rounded-full hover:bg-slate-200/50 transition-all duration-200"
          >
            Features
          </a>
          <a
            href="#how-it-works"
            className="text-slate-600 hover:text-slate-900 text-sm font-medium px-4 py-2 rounded-full hover:bg-slate-200/50 transition-all duration-200"
          >
            How it Works
          </a>
        </nav>

        {/* Login Button Group */}
        <div className="relative flex items-center gap-3 z-20">
          <button 
            onClick={() => navigate('/login')}
            className="hidden sm:block px-5 py-2 rounded-full bg-white text-slate-700 font-medium text-sm transition-all shadow-sm border border-slate-200 hover:bg-slate-50 cursor-pointer"
          >
            Sign In
          </button>
          <button 
            onClick={() => navigate('/signup')}
            className="px-6 py-2.5 rounded-full bg-slate-900 text-white font-medium text-sm transition-all shadow-lg hover:bg-slate-800 hover:shadow-xl hover:-translate-y-0.5 cursor-pointer"
          >
            Get Started
          </button>
        </div>
      </header>

      <main className="relative z-20 flex-1 flex items-center px-6 md:px-16 mt-12 md:mt-0">
        <div className="text-left max-w-4xl">
          <motion.div
            className="inline-flex items-center px-4 py-2 rounded-full bg-white/40 backdrop-blur-md mb-6 relative border border-white/60 shadow-sm"
            style={{ filter: "url(#glass-effect)" }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <span className="text-slate-800 text-sm font-semibold relative z-10 tracking-wide">
              ✨ The Future of Policy Simulation
            </span>
          </motion.div>

          <motion.h1
            className="text-4xl md:text-7xl lg:text-8xl font-bold text-slate-900 mb-6 leading-[1.1] tracking-tight"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <motion.span
              className="block font-light text-slate-800 text-3xl md:text-5xl lg:text-6xl mb-2 tracking-wider"
              style={{
                background: "linear-gradient(135deg, #0ea5e9 0%, #3b82f6 30%, #2563eb 70%, #1e40af 100%)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                backgroundClip: "text",
              }}
              animate={{ backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"] }}
              transition={{ duration: 8, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
            >
              Simulate Policy.
            </motion.span>
            <span className="block font-black drop-shadow-sm">Predict Reality.</span>
          </motion.h1>

          <motion.p
            className="text-xl md:text-2xl font-light text-slate-700 mb-10 leading-relaxed max-w-2xl"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
          >
            Test economic policies before they're enacted. Our AI engine predicts GDP, inflation, employment and environmental impact in milliseconds.
          </motion.p>

          <motion.div
            className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 w-full sm:w-auto mt-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 1.0 }}
          >
            <motion.button
              onClick={() => navigate('/signup')}
              className="w-full sm:w-auto px-8 py-4 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold text-base transition-all duration-300 hover:from-cyan-400 hover:to-blue-500 cursor-pointer shadow-lg hover:shadow-cyan-500/25"
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
            >
              Start Simulating
            </motion.button>
            <motion.a
              href="#features"
              className="w-full sm:w-auto text-center px-8 py-4 rounded-full bg-white/50 border border-slate-200/60 text-slate-700 font-medium text-base transition-all duration-300 hover:bg-white/80 hover:border-slate-300 cursor-pointer backdrop-blur-sm"
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
            >
              Explore Features
            </motion.a>
          </motion.div>
        </div>
      </main>

      <div className="hidden lg:block absolute bottom-12 right-16 z-30">
        <div className="relative w-24 h-24 flex items-center justify-center">
          <PulsingBorder
            colors={["#0ea5e9", "#3b82f6", "#2563eb", "#60a5fa", "#38bdf8", "#0284c7"]}
            colorBack="#ffffff00"
            speed={1.5}
            roundness={1}
            thickness={0.15}
            softness={0.2}
            intensity={4}
            spotsPerColor={4}
            spotSize={0.15}
            pulse={0.1}
            smoke={0.3}
            smokeSize={3}
            scale={0.8}
            rotation={0}
            frame={0}
            style={{
              width: "70px",
              height: "70px",
              borderRadius: "50%",
            }}
          />

          <motion.svg
            className="absolute inset-0 w-full h-full"
            viewBox="0 0 100 100"
            animate={{ rotate: 360 }}
            transition={{
              duration: 25,
              repeat: Number.POSITIVE_INFINITY,
              ease: "linear",
            }}
            style={{ transform: "scale(1.5)" }}
          >
            <defs>
              <path id="circle" d="M 50, 50 m -35, 0 a 35,35 0 1,1 70,0 a 35,35 0 1,1 -70,0" />
            </defs>
            <text className="text-[11px] fill-slate-500 font-bold tracking-widest uppercase">
              <textPath href="#circle" startOffset="0%">
                Machine Learning • Real-Time Engine • 94% Accuracy •
              </textPath>
            </text>
          </motion.svg>
        </div>
      </div>
    </div>
  )
}
