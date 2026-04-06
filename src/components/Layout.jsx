import React from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, Sliders, BarChart3, GitCompare, 
  Activity, LogOut, Zap, Brain, ChevronRight
} from 'lucide-react'

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/simulator', label: 'Policy Simulator', icon: Sliders },
  { path: '/results', label: 'Simulation Results', icon: BarChart3 },
  { path: '/scenarios', label: 'Scenario Comparison', icon: GitCompare },
]

export default function Layout({ children, onLogout }) {
  const location = useLocation()
  const [collapsed, setCollapsed] = React.useState(false)

  return (
    <div className="flex h-screen overflow-hidden bg-dark-500">
      {/* Sidebar */}
      <aside className={`${collapsed ? 'w-20' : 'w-72'} flex-shrink-0 bg-dark-400 border-r border-white/5 flex flex-col transition-all duration-300`}>
        {/* Logo */}
        <div className="p-6 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center flex-shrink-0">
            <Brain className="w-5 h-5 text-white" />
          </div>
          {!collapsed && (
            <div>
              <h1 className="font-display font-bold text-lg text-white">PolicyAI</h1>
              <p className="text-xs text-gray-500">Impact Simulator</p>
            </div>
          )}
        </div>

        {/* Nav Links */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map(({ path, label, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === '/'}
              className={({ isActive }) =>
                `nav-link ${isActive ? 'active' : ''}`
              }
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {!collapsed && <span className="text-sm font-medium">{label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* Status Widget */}
        {!collapsed && (
          <div className="mx-3 mb-4 p-4 rounded-xl bg-dark-300 border border-white/5">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs font-medium text-emerald-400">ML Engine Online</span>
            </div>
            <div className="space-y-2 text-xs text-gray-400">
              <div className="flex justify-between">
                <span>Model</span>
                <span className="text-gray-200">Random Forest</span>
              </div>
              <div className="flex justify-between">
                <span>Accuracy</span>
                <span className="text-primary-400 font-semibold">94.2%</span>
              </div>
              <div className="flex justify-between">
                <span>Dataset</span>
                <span className="text-gray-200">5,000 samples</span>
              </div>
            </div>
          </div>
        )}

        {/* Logout */}
        <div className="p-3 border-t border-white/5">
          <button
            onClick={onLogout}
            className="nav-link w-full text-red-400 hover:text-red-300 hover:bg-red-500/10"
          >
            <LogOut className="w-5 h-5 flex-shrink-0" />
            {!collapsed && <span className="text-sm font-medium">Sign Out</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        {/* Top Bar */}
        <header className="sticky top-0 z-40 bg-dark-500/80 backdrop-blur-xl border-b border-white/5 px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => setCollapsed(!collapsed)}
              className="p-2 rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition-colors"
            >
              <ChevronRight className={`w-4 h-4 transition-transform ${collapsed ? '' : 'rotate-180'}`} />
            </button>
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
              <Activity className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-xs font-medium text-emerald-400">ML Engine Online</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="px-3 py-1.5 rounded-full bg-primary-500/10 border border-primary-500/20">
              <span className="text-xs font-medium text-primary-400">
                <Zap className="w-3 h-3 inline mr-1" />
                Random Forest v2.4
              </span>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="p-8 bg-grid min-h-[calc(100vh-73px)]">
          {children}
        </div>
      </main>
    </div>
  )
}
