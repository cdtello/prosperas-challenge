export type JobStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED'

export interface Job {
  job_id: string
  user_id: string
  status: JobStatus
  report_type: string
  date_range: string
  format: string
  created_at: string
  updated_at: string
  result_url: string | null
}

export interface PaginatedJobs {
  items: Job[]
  total: number
  page: number
  page_size: number
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface CreateJobPayload {
  report_type: string
  date_range: string
  format: string
}
