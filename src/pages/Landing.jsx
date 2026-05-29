import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Brain, LineChart, Database, Zap, Globe, Users, TrendingUp, ShieldCheck } from 'lucide-react';

const FadeIn = ({ children, delay = 0, duration = 1000, className = '' }) => {
  const [visible, setVisible] = useState(false);
  
  useEffect(() => {
    const timer = setTimeout(() => setVisible(true), delay);
    return () => clearTimeout(timer);
  }, [delay]);
  
  return (
    <div
      className={`transition-opacity ${className}`}
      style={{
        opacity: visible ? 1 : 0,
        transitionDuration: `${duration}ms`
      }}
    >
      {children}
    </div>
  );
};

const AnimatedHeading = ({ text, initialDelay = 200 }) => {
  const [start, setStart] = useState(false);
  
  useEffect(() => {
    const timer = setTimeout(() => setStart(true), initialDelay);
    return () => clearTimeout(timer);
  }, [initialDelay]);

  const lines = text.split('\n');

  return (
    <>
      {lines.map((line, lineIndex) => {
        const lineLength = line.length;
        return (
          <div key={lineIndex} className="block">
            {line.split('').map((char, charIndex) => {
              const charDelay = 30;
              const delay = (lineIndex * lineLength * charDelay) + (charIndex * charDelay);
              
              return (
                <span
                  key={charIndex}
                  className="inline-block transition-all"
                  style={{
                    opacity: start ? 1 : 0,
                    transform: start ? 'translateX(0)' : 'translateX(-18px)',
                    transitionDuration: '500ms',
                    transitionDelay: `${delay}ms`
                  }}
                >
                  {char === ' ' ? '\u00A0' : char}
                </span>
              );
            })}
          </div>
        );
      })}
    </>
  );
};

export default function Landing() {
  return (
    <div className="relative w-full h-screen overflow-y-auto text-white font-sans snap-y snap-mandatory">
      {/* --- HERO SECTION --- */}
      <section className="relative z-10 flex flex-col w-full min-h-screen snap-start">
        {/* Navbar */}
        <div className="px-6 md:px-12 lg:px-16 pt-6">
          <nav className="liquid-glass rounded-xl px-4 py-2 flex items-center justify-between">
            <div className="text-2xl font-semibold tracking-tight">VEX</div>
            
            <div className="hidden md:flex items-center gap-8 text-sm">
              <a href="#features" className="hover:text-gray-300 transition-colors">Features</a>
              <Link to="/login" className="hover:text-gray-300 transition-colors">Simulator</Link>
              <Link to="/login" className="hover:text-gray-300 transition-colors">Advisory</Link>
            </div>

            <Link to="/login" className="bg-white text-black px-6 py-2 rounded-lg text-sm font-medium hover:bg-gray-100 transition-colors">
              Start a Chat
            </Link>
          </nav>
        </div>

        {/* Hero Content */}
        <div className="px-6 md:px-12 lg:px-16 flex-1 flex flex-col justify-end pb-12 lg:pb-16">
          <div className="lg:grid lg:grid-cols-2 lg:items-end">
            
            {/* Left Column */}
            <div className="w-full">
              <h1 
                className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-normal mb-4"
                style={{ letterSpacing: '-0.04em' }}
              >
                <AnimatedHeading text={"Shaping tomorrow\nwith vision and action."} />
              </h1>
              
              <FadeIn delay={800} duration={1000}>
                <p className="text-base md:text-lg text-gray-300 mb-5 max-w-2xl">
                  We back visionaries and craft ventures that define what comes next. Harness the power of AI to forecast economic policy impact.
                </p>
              </FadeIn>

              <FadeIn delay={1200} duration={1000} className="flex flex-wrap gap-4">
                <Link to="/login" className="bg-white text-black px-8 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors">
                  Start a Chat
                </Link>
                <a href="#features" className="liquid-glass border border-white/20 text-white px-8 py-3 rounded-lg font-medium hover:bg-white hover:text-black transition-all">
                  Explore Features
                </a>
              </FadeIn>
            </div>

            {/* Right Column */}
            <div className="flex items-end justify-start lg:justify-end mt-8 lg:mt-0">
              <FadeIn delay={1400} duration={1000}>
                <div className="liquid-glass border border-white/20 px-6 py-3 rounded-xl">
                  <span className="text-lg md:text-xl lg:text-2xl font-light">
                    Predicting. Simulating. Adapting.
                  </span>
                </div>
              </FadeIn>
            </div>

          </div>
        </div>
      </section>

      {/* --- FEATURES SECTION --- */}
      <section id="features" className="relative z-10 w-full min-h-screen snap-start flex flex-col justify-center px-6 md:px-12 lg:px-16 py-20">
        <div className="max-w-7xl mx-auto w-full">
          <div className="mb-16">
            <h2 className="text-3xl md:text-5xl font-normal mb-6 tracking-tight">Intelligence at scale.</h2>
            <p className="text-gray-300 text-lg max-w-2xl">
              Nexora provides unparalleled predictive capabilities, allowing you to simulate policy changes and instantly see the macroeconomic ripple effects.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Feature 1 */}
            <div className="liquid-glass border border-white/10 rounded-2xl p-8 hover:bg-white/10 transition-colors">
              <Brain className="w-10 h-10 text-white mb-6" />
              <h3 className="text-xl font-medium mb-3">Predictive AI Engine</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Powered by a fine-tuned Random Forest Regressor, forecasting GDP, inflation, and employment shifts with remarkable accuracy.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="liquid-glass border border-white/10 rounded-2xl p-8 hover:bg-white/10 transition-colors">
              <Zap className="w-10 h-10 text-white mb-6" />
              <h3 className="text-xl font-medium mb-3">Scenario Sandbox</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Tweak interest rates, subsidies, and tax policies in an isolated environment to discover optimal macroeconomic strategies.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="liquid-glass border border-white/10 rounded-2xl p-8 hover:bg-white/10 transition-colors">
              <Database className="w-10 h-10 text-white mb-6" />
              <h3 className="text-xl font-medium mb-3">Real-world Data</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Continuously trained on authentic global economic datasets, ensuring your insights are grounded in reality.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="liquid-glass border border-white/10 rounded-2xl p-8 hover:bg-white/10 transition-colors">
              <LineChart className="w-10 h-10 text-white mb-6" />
              <h3 className="text-xl font-medium mb-3">Instant Visualizations</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Dynamic sensitivity analysis and feature importance metrics delivered through sleek, interactive dashboard components.
              </p>
            </div>
          </div>
          
          <div className="mt-20 flex justify-center">
             <Link to="/login" className="bg-white text-black px-10 py-4 rounded-xl font-medium hover:scale-105 transition-transform duration-300">
                Launch Simulator
             </Link>
          </div>
        </div>
      </section>

      {/* --- CORE METRICS SECTION --- */}
      <section className="relative z-10 w-full min-h-[80vh] snap-start flex flex-col justify-center px-6 md:px-12 lg:px-16 py-20 bg-black/40">
        <div className="max-w-7xl mx-auto w-full">
          <div className="mb-16 text-center">
            <h2 className="text-3xl md:text-5xl font-normal mb-6 tracking-tight">Simulate 5 Key Macro-Outcomes.</h2>
            <p className="text-gray-300 text-lg max-w-2xl mx-auto">
              Our MultiOutput Random Forest Engine predicts precisely how your policy adjustments will impact the economy and society.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
            <div className="liquid-glass border border-white/10 rounded-2xl p-6">
              <TrendingUp className="w-8 h-8 text-cyan-400 mx-auto mb-4" />
              <h4 className="font-medium">GDP Growth</h4>
            </div>
            <div className="liquid-glass border border-white/10 rounded-2xl p-6">
              <TrendingUp className="w-8 h-8 text-red-400 mx-auto mb-4" />
              <h4 className="font-medium">Inflation</h4>
            </div>
            <div className="liquid-glass border border-white/10 rounded-2xl p-6">
              <Users className="w-8 h-8 text-emerald-400 mx-auto mb-4" />
              <h4 className="font-medium">Employment</h4>
            </div>
            <div className="liquid-glass border border-white/10 rounded-2xl p-6">
              <Globe className="w-8 h-8 text-green-400 mx-auto mb-4" />
              <h4 className="font-medium">Environment</h4>
            </div>
            <div className="liquid-glass border border-white/10 rounded-2xl p-6">
              <ShieldCheck className="w-8 h-8 text-amber-400 mx-auto mb-4" />
              <h4 className="font-medium">Satisfaction</h4>
            </div>
          </div>
        </div>
      </section>

      {/* --- USE CASES SECTION --- */}
      <section className="relative z-10 w-full min-h-screen snap-start flex flex-col justify-center px-6 md:px-12 lg:px-16 py-20">
        <div className="max-w-7xl mx-auto w-full">
          <div className="mb-16">
            <h2 className="text-3xl md:text-5xl font-normal mb-6 tracking-tight">Who is Nexora for?</h2>
            <p className="text-gray-300 text-lg max-w-2xl">
              Empowering decision-makers across sectors with actionable economic foresight.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="border-l-2 border-white/20 pl-6 hover:border-white transition-colors">
              <h3 className="text-xl font-medium mb-3">Government Entities</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Test tax rates and public spending allocations in a risk-free environment before drafting legislation, ensuring optimal public satisfaction and stable growth.
              </p>
            </div>
            <div className="border-l-2 border-white/20 pl-6 hover:border-white transition-colors">
              <h3 className="text-xl font-medium mb-3">Financial Institutions</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Stress-test portfolios against simulated macroeconomic shocks, predicting inflation trends and interest rate shifts to stay ahead of the market.
              </p>
            </div>
            <div className="border-l-2 border-white/20 pl-6 hover:border-white transition-colors">
              <h3 className="text-xl font-medium mb-3">Policy Think Tanks</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Generate data-backed proposals and visually compelling reports. Export simulation results to PDF instantly for stakeholder presentations.
              </p>
            </div>
          </div>

          <div className="mt-32 pb-12 flex flex-col items-center text-center">
            <h2 className="text-4xl font-semibold mb-8 tracking-tight">Ready to shape the future?</h2>
            <Link to="/login" className="bg-white text-black px-12 py-5 rounded-xl text-lg font-medium hover:scale-105 transition-transform duration-300">
              Get Started Now
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
