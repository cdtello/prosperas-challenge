import { type InputHTMLAttributes } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

export function Input({ label, error, className = '', ...props }: InputProps) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">
          {label}
        </label>
      )}
      <input
        className={`
          w-full px-4 py-2.5 rounded-xl text-sm text-slate-100
          bg-white/5 border border-white/10
          placeholder:text-slate-600
          focus:outline-none focus:border-accent/60 focus:bg-white/7
          transition-all duration-200
          ${error ? 'border-red-500/50 focus:border-red-500/70' : ''}
          ${className}
        `}
        {...props}
      />
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  )
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  children: React.ReactNode
}

export function Select({ label, children, className = '', ...props }: SelectProps) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">
          {label}
        </label>
      )}
      <select
        className={`
          w-full px-4 py-2.5 rounded-xl text-sm text-slate-100
          bg-dark-card border border-white/10
          focus:outline-none focus:border-accent/60
          transition-all duration-200 cursor-pointer
          ${className}
        `}
        {...props}
      >
        {children}
      </select>
    </div>
  )
}
