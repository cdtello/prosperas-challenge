export function Spinner({ className = '' }: { className?: string }) {
  return (
    <div className={`relative ${className}`}>
      <div className="w-8 h-8 rounded-full border-2 border-white/10" />
      <div className="absolute inset-0 w-8 h-8 rounded-full border-2 border-transparent border-t-accent animate-spin" />
    </div>
  )
}

export function PageSpinner() {
  return (
    <div className="flex items-center justify-center h-64">
      <Spinner />
    </div>
  )
}
