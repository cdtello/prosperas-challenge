import { motion } from 'framer-motion'
import { type ReactNode } from 'react'

interface CardProps {
  children: ReactNode
  className?: string
  hover?: boolean
  glow?: boolean
}

export function Card({ children, className = '', hover = false, glow = false }: CardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`
        glass rounded-2xl p-6
        ${hover ? 'glass-hover cursor-pointer' : ''}
        ${glow ? 'glow-accent' : ''}
        ${className}
      `}
    >
      {children}
    </motion.div>
  )
}

export function CardHeader({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <div className={`flex items-center justify-between mb-4 ${className}`}>
      {children}
    </div>
  )
}
