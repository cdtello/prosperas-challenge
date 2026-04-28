import { motion } from 'framer-motion'
import { Calendar, ExternalLink, FileText } from 'lucide-react'
import type { Job } from '@/shared/types'
import { JobBadge } from './JobBadge'

interface JobCardProps {
  job: Job
  index: number
}

export function JobCard({ job, index }: JobCardProps) {
  const createdAt = new Date(job.created_at).toLocaleString()

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04, duration: 0.3 }}
      layout
      className="glass glass-hover rounded-2xl p-5 group"
    >
      <div className="flex items-start justify-between gap-4">
        {/* Icon + info */}
        <div className="flex items-start gap-4 min-w-0">
          <div className="w-10 h-10 rounded-xl bg-accent/10 border border-accent/20 flex items-center justify-center flex-shrink-0 group-hover:bg-accent/15 transition-colors">
            <FileText className="w-5 h-5 text-accent-glow" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-slate-200 truncate capitalize">
              {job.report_type.replace(/_/g, ' ')}
            </p>
            <div className="flex items-center gap-2 mt-1">
              <Calendar className="w-3 h-3 text-slate-600" />
              <span className="text-xs text-slate-500">{job.date_range}</span>
              <span className="text-slate-700">·</span>
              <span className="text-xs text-slate-500 uppercase">{job.format}</span>
            </div>
            <p className="text-xs text-slate-600 mt-1.5">{createdAt}</p>
          </div>
        </div>

        {/* Badge + link */}
        <div className="flex flex-col items-end gap-2 flex-shrink-0">
          <JobBadge status={job.status} />
          {job.result_url && (
            <a
              href={job.result_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-xs text-accent-glow hover:text-white transition-colors"
            >
              <ExternalLink className="w-3 h-3" />
              View report
            </a>
          )}
        </div>
      </div>

      {/* Progress bar for PROCESSING */}
      {job.status === 'PROCESSING' && (
        <div className="mt-4 h-0.5 bg-white/5 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-cyan-500 to-accent rounded-full"
            animate={{ x: ['-100%', '100%'] }}
            transition={{ repeat: Infinity, duration: 1.5, ease: 'easeInOut' }}
          />
        </div>
      )}
    </motion.div>
  )
}
