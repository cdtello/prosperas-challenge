import { AnimatePresence, motion } from 'framer-motion'
import { RefreshCw } from 'lucide-react'
import { Layout } from '@/shared/ui/Layout'
import { PageSpinner } from '@/shared/ui/Spinner'
import { CreateJobForm } from './CreateJobForm'
import { JobCard } from './JobCard'
import { StatsBar } from './StatsBar'
import { useJobs } from '../model/useJobs'

export function JobsPage() {
  const { data, isLoading, isFetching } = useJobs()
  const jobs = data?.items ?? []

  return (
    <Layout>
      <div className="flex flex-col gap-6">

        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gradient">Reports Dashboard</h1>
            <p className="text-slate-500 text-sm mt-1">
              Generate and monitor async reports in real time
            </p>
          </div>
          <div className="flex items-center gap-2">
            <AnimatePresence>
              {isFetching && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl glass text-xs text-slate-400"
                >
                  <RefreshCw className="w-3 h-3 animate-spin text-accent-glow" />
                  Syncing
                </motion.div>
              )}
            </AnimatePresence>
            <div className="px-3 py-1.5 rounded-xl glass text-xs text-slate-500">
              Auto-refresh 3s
            </div>
          </div>
        </div>

        {/* Stats */}
        {!isLoading && <StatsBar jobs={jobs} />}

        {/* Main grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Create form */}
          <div className="lg:col-span-1">
            <CreateJobForm />
          </div>

          {/* Jobs list */}
          <div className="lg:col-span-2">
            <div className="glass rounded-2xl p-5">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-semibold text-slate-200">
                  Recent Reports
                  {data?.total !== undefined && (
                    <span className="ml-2 text-xs text-slate-500 font-normal">({data.total})</span>
                  )}
                </h2>
              </div>

              {isLoading ? (
                <PageSpinner />
              ) : jobs.length === 0 ? (
                <EmptyState />
              ) : (
                <div className="flex flex-col gap-3">
                  <AnimatePresence mode="popLayout">
                    {jobs.map((job, i) => (
                      <JobCard key={job.job_id} job={job} index={i} />
                    ))}
                  </AnimatePresence>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

function EmptyState() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex flex-col items-center justify-center py-16 text-center"
    >
      <div className="w-16 h-16 rounded-2xl bg-white/3 border border-white/07 flex items-center justify-center mb-4">
        <RefreshCw className="w-7 h-7 text-slate-600" />
      </div>
      <p className="text-slate-400 font-medium">No reports yet</p>
      <p className="text-slate-600 text-sm mt-1">Create your first report using the form</p>
    </motion.div>
  )
}
