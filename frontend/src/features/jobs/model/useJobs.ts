import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import type { CreateJobPayload } from '@/shared/types'
import { jobsApi } from '../api/jobsApi'

export function useJobs(page = 1) {
  return useQuery({
    queryKey: ['jobs', page],
    queryFn: () => jobsApi.list(page).then(r => r.data),
    refetchInterval: 3000,
    refetchIntervalInBackground: true,
  })
}

export function useCreateJob() {
  const qc = useQueryClient()

  return useMutation({
    mutationFn: (payload: CreateJobPayload) => jobsApi.create(payload).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['jobs'] })
      toast.success('Report queued successfully!')
    },
    onError: () => {
      toast.error('Failed to create report')
    },
  })
}
