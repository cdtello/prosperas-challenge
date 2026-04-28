import { motion } from 'framer-motion'
import { Loader2 } from 'lucide-react'
import { type ButtonHTMLAttributes, type ReactNode } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode
  variant?: 'primary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
}

const variants = {
  primary: 'bg-accent text-white shadow-accent hover:bg-accent-dark hover:shadow-accent-lg',
  ghost: 'glass text-slate-300 hover:text-white hover:border-white/20',
  danger: 'bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30',
}

const sizes = {
  sm: 'px-3 py-1.5 text-xs rounded-lg',
  md: 'px-4 py-2 text-sm rounded-xl',
  lg: 'px-6 py-3 text-base rounded-xl',
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled,
  className = '',
  ...props
}: ButtonProps) {
  return (
    <motion.button
      whileTap={{ scale: 0.97 }}
      className={`
        inline-flex items-center justify-center gap-2 font-medium
        transition-all duration-200 cursor-pointer
        disabled:opacity-40 disabled:cursor-not-allowed
        ${variants[variant]} ${sizes[size]} ${className}
      `}
      disabled={disabled || loading}
      {...(props as React.ComponentProps<typeof motion.button>)}
    >
      {loading && <Loader2 className="w-4 h-4 animate-spin" />}
      {children}
    </motion.button>
  )
}
