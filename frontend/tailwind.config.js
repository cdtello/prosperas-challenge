/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#050b1f',
          surface: '#080f24',
          card: '#0d1730',
          border: 'rgba(255,255,255,0.07)',
        },
        accent: {
          DEFAULT: '#3b82f6',
          dark: '#1d4ed8',
          glow: '#60a5fa',
          dim: 'rgba(59,130,246,0.15)',
        },
        status: {
          pending: '#f59e0b',
          processing: '#06b6d4',
          completed: '#10b981',
          failed: '#ef4444',
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'mesh': 'linear-gradient(135deg, #050b1f 0%, #0a1628 50%, #050b1f 100%)',
      },
      backdropBlur: {
        xs: '4px',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(59,130,246,0.3)' },
          '100%': { boxShadow: '0 0 20px rgba(59,130,246,0.6), 0 0 40px rgba(59,130,246,0.2)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
      },
      boxShadow: {
        'glass': '0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06)',
        'glass-lg': '0 16px 48px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.08)',
        'accent': '0 0 20px rgba(59,130,246,0.4)',
        'accent-lg': '0 0 40px rgba(59,130,246,0.3)',
      },
    },
  },
  plugins: [],
}
