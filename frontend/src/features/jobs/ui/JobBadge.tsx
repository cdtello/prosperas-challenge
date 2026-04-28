import { motion } from 'framer-motion'
import type { JobStatus } from '@/shared/types'

const config: Record<JobStatus, { label: string; classes: string; dot: string }> = {
  PENDING: {
    label: 'Pending',
    classes: 'bg-amber-500/15 text-amber-300 border-amber-500/25',
    dot: 'bg-amber-400',
  },
  PROCESSING: {
    label: 'Processing',
    classes: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/25',
    dot: 'bg-cyan-400 animate-pulse',
  },
  COMPLETED: {
    label: 'Completed',
    classes: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/25',
    dot: 'bg-emerald-400',
  },
  FAILED: {
    label: 'Failed',
    classes: 'bg-red-500/15 text-red-300 border-red-500/25',
    dot: 'bg-red-400',
  },
}

export function JobBadge({ status }: { status: JobStatus }) {
  const { label, classes, dot } = config[status]
  return (
    <motion.span
      layout
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${classes}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dot}`} />
      {label}
    </motion.span>
  )
}
