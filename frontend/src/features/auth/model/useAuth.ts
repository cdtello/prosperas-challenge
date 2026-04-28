import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { authApi } from '../api/authApi'
import { useAuthContext } from './authContext'

export function useAuth() {
  const { saveToken, logout } = useAuthContext()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)

  const login = async (username: string, password: string) => {
    setLoading(true)
    try {
      const { data } = await authApi.login(username, password)
      saveToken(data.access_token)
      navigate('/jobs')
      toast.success('Welcome back!')
    } catch {
      toast.error('Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  const register = async (username: string, email: string, password: string) => {
    setLoading(true)
    try {
      const { data } = await authApi.register(username, email, password)
      saveToken(data.access_token)
      navigate('/jobs')
      toast.success('Account created!')
    } catch {
      toast.error('Username already taken')
    } finally {
      setLoading(false)
    }
  }

  return { login, register, logout, loading }
}
