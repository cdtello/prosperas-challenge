import { api } from '@/shared/lib/axios'
import type { CreateJobPayload, Job, PaginatedJobs } from '@/shared/types'

export const jobsApi = {
  create: (payload: CreateJobPayload) =>
    api.post<Job>('/jobs', payload),

  getById: (jobId: string) =>
    api.get<Job>(`/jobs/${jobId}`),

  list: (page = 1, pageSize = 20) =>
    api.get<PaginatedJobs>('/jobs', { params: { page, page_size: pageSize } }),
}
