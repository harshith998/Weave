/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Base colors
        bg: {
          primary: '#1A1A1D',
          secondary: '#252528',
          tertiary: '#2D2D32',
        },
        text: {
          primary: '#EEEFF1',
          secondary: '#9CA3AF',
          tertiary: '#6B7280',
        },
        border: {
          subtle: 'rgba(255, 255, 255, 0.08)',
          light: 'rgba(255, 255, 255, 0.12)',
        },
        // Status colors
        status: {
          completed: '#10B981',
          progress: '#F59E0B',
          pending: '#3B82F6',
          active: '#8B5CF6',
          error: '#EF4444',
        },
        // Glass
        glass: {
          bg: 'rgba(37, 37, 40, 0.6)',
          border: 'rgba(255, 255, 255, 0.1)',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'xs': ['11px', '16px'],
        'sm': ['12px', '18px'],
        'base': ['14px', '21px'],
        'lg': ['16px', '24px'],
        'xl': ['18px', '24px'],
        '2xl': ['24px', '32px'],
      },
      spacing: {
        'xs': '4px',
        'sm': '8px',
        'md': '12px',
        'lg': '16px',
        'xl': '24px',
        '2xl': '32px',
        '3xl': '48px',
        '4xl': '64px',
      },
      backdropBlur: {
        xs: '8px',
        sm: '12px',
        md: '16px',
        lg: '20px',
      },
      boxShadow: {
        'glass': '0 8px 32px rgba(0, 0, 0, 0.2)',
        'glow-purple': '0 0 20px rgba(139, 92, 246, 0.4)',
        'glow-orange': '0 0 20px rgba(245, 158, 11, 0.4)',
        'glow-blue': '0 0 20px rgba(59, 130, 246, 0.4)',
        'glow-green': '0 0 20px rgba(16, 185, 129, 0.4)',
      },
      animation: {
        'pulse-slow': 'pulse 2s ease-in-out infinite',
        'glow': 'glow 3s ease-in-out infinite',
        'shimmer': 'shimmer 2s infinite',
      },
      keyframes: {
        glow: {
          '0%, 100%': {
            boxShadow: '0 0 20px rgba(139, 92, 246, 0.4), 0 0 0 4px rgba(139, 92, 246, 0.1)'
          },
          '50%': {
            boxShadow: '0 0 30px rgba(139, 92, 246, 0.6), 0 0 0 6px rgba(139, 92, 246, 0.15)'
          },
        },
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
      },
    },
  },
  plugins: [],
}
