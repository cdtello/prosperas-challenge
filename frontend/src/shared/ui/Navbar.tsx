import { motion } from 'framer-motion'
import { BarChart3, LogOut, User } from 'lucide-react'
import { useAuth } from '@/features/auth/model/useAuth'

export function Navbar() {
  const { logout } = useAuth()

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="fixed top-0 left-0 right-0 z-50 h-16"
    >
      <div className="glass-strong h-full px-6 flex items-center justify-between border-b border-white/07">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-accent/20 border border-accent/30 flex items-center justify-center glow-accent">
            <BarChart3 className="w-4 h-4 text-accent-glow" />
          </div>
          <div>
            <span className="text-gradient-accent font-bold text-lg tracking-tight">Prosperas</span>
            <span className="text-slate-500 text-xs ml-2">Reports</span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl glass">
            <div className="w-2 h-2 rounded-full bg-status-completed animate-pulse" />
            <span className="text-xs text-slate-400">Live</span>
          </div>

          <button className="w-8 h-8 rounded-xl glass flex items-center justify-center text-slate-400 hover:text-slate-200 transition-colors">
            <User className="w-4 h-4" />
          </button>

          <button
            onClick={logout}
            className="w-8 h-8 rounded-xl glass flex items-center justify-center text-slate-500 hover:text-red-400 transition-colors"
            title="Logout"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </motion.header>
  )
}
