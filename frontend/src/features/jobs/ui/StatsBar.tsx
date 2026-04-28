import { motion } from 'framer-motion'
import { CheckCircle2, Clock, Loader, XCircle } from 'lucide-react'
import type { Job } from '@/shared/types'

interface StatsBarProps {
  jobs: Job[]
}

export function StatsBar({ jobs }: StatsBarProps) {
  const counts = {
    PENDING: jobs.filter(j => j.status === 'PENDING').length,
    PROCESSING: jobs.filter(j => j.status === 'PROCESSING').length,
    COMPLETED: jobs.filter(j => j.status === 'COMPLETED').length,
    FAILED: jobs.filter(j => j.status === 'FAILED').length,
  }

  const stats = [
    { label: 'Total', value: jobs.length, icon: null, color: 'text-slate-300', bg: 'bg-slate-500/10 border-slate-500/20' },
    { label: 'Pending', value: counts.PENDING, icon: Clock, color: 'text-amber-300', bg: 'bg-amber-500/10 border-amber-500/20' },
    { label: 'Processing', value: counts.PROCESSING, icon: Loader, color: 'text-cyan-300', bg: 'bg-cyan-500/10 border-cyan-500/20' },
    { label: 'Completed', value: counts.COMPLETED, icon: CheckCircle2, color: 'text-emerald-300', bg: 'bg-emerald-500/10 border-emerald-500/20' },
    { label: 'Failed', value: counts.FAILED, icon: XCircle, color: 'text-red-300', bg: 'bg-red-500/10 border-red-500/20' },
  ]

  return (
    <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
      {stats.map((stat, i) => (
        <motion.div
          key={stat.label}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.06 }}
          className={`glass rounded-2xl p-4 border ${stat.bg}`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-500">{stat.label}</span>
            {stat.icon && <stat.icon className={`w-3.5 h-3.5 ${stat.color} ${stat.label === 'Processing' && counts.PROCESSING > 0 ? 'animate-spin' : ''}`} />}
          </div>
          <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
        </motion.div>
      ))}
    </div>
  )
}
