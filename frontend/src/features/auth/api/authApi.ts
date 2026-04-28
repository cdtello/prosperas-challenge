import { api } from '@/shared/lib/axios'
import type { TokenResponse } from '@/shared/types'

export const authApi = {
  register: (username: string, email: string, password: string) =>
    api.post<TokenResponse>('/auth/register', { username, email, password }),

  login: (username: string, password: string) =>
    api.post<TokenResponse>('/auth/login', { username, password }),
}
