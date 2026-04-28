import { motion } from 'framer-motion'
import { BarChart3, Lock, Mail, User } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/shared/ui/Button'
import { Input } from '@/shared/ui/Input'
import { useAuth } from '../model/useAuth'

export function RegisterPage() {
  const { register, loading } = useAuth()
  const [form, setForm] = useState({ username: '', email: '', password: '' })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    register(form.username, form.email, form.password)
  }

  return (
    <div className="min-h-screen bg-mesh flex items-center justify-center p-4">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-accent/5 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-1/3 left-1/4 w-80 h-80 bg-purple-500/3 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1.5s' }} />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-accent/10 border border-accent/20 mb-4 glow-accent"
          >
            <BarChart3 className="w-8 h-8 text-accent-glow" />
          </motion.div>
          <h1 className="text-2xl font-bold text-gradient">Create Account</h1>
          <p className="text-slate-500 text-sm mt-1">Start generating reports today</p>
        </div>

        <div className="glass-strong rounded-3xl p-8">
          <form onSubmit={handleSubmit} className="flex flex-col gap-5">
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 mt-3" />
              <Input
                label="Username"
                placeholder="your_username"
                value={form.username}
                onChange={e => setForm(f => ({ ...f, username: e.target.value }))}
                className="pl-10"
                required
              />
            </div>

            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 mt-3" />
              <Input
                label="Email"
                type="email"
                placeholder="you@example.com"
                value={form.email}
                onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
                className="pl-10"
                required
              />
            </div>

            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 mt-3" />
              <Input
                label="Password"
                type="password"
                placeholder="••••••••"
                value={form.password}
                onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                className="pl-10"
                required
              />
            </div>

            <Button type="submit" size="lg" loading={loading} className="mt-2 w-full glow-accent">
              Create Account
            </Button>
          </form>

          <div className="mt-6 pt-6 border-t border-white/07 text-center">
            <p className="text-slate-500 text-sm">
              Already have an account?{' '}
              <Link to="/login" className="text-accent-glow hover:text-white transition-colors font-medium">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
