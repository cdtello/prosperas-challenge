import { createContext, useCallback, useContext, useState, type ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'

interface AuthContextValue {
  token: string | null
  isAuthenticated: boolean
  saveToken: (token: string) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'))
  const navigate = useNavigate()

  const saveToken = useCallback((t: string) => {
    localStorage.setItem('token', t)
    setToken(t)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('token')
    setToken(null)
    navigate('/login')
  }, [navigate])

  return (
    <AuthContext.Provider value={{ token, isAuthenticated: !!token, saveToken, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuthContext() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuthContext must be used inside AuthProvider')
  return ctx
}
