/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Bloomberg Terminal-inspired dark theme
        primary: {
          bg: '#0A0E27',
          surface: '#131722',
          elevated: '#1E2330',
          hover: '#252A3A',
          border: '#2A2E39',
        },
        text: {
          primary: '#E0E3EB',
          secondary: '#848E9C',
          tertiary: '#5E6673',
        },
        accent: {
          blue: '#2962FF',
          'blue-hover': '#1E53E5',
        },
        semantic: {
          positive: '#26A69A',
          negative: '#EF5350',
          warning: '#FF9800',
        },
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'SF Pro Display', 'Helvetica Neue', 'sans-serif'],
        mono: ['SF Mono', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      fontSize: {
        'xs': '0.6875rem',     // 11px
        'sm': '0.8125rem',     // 13px
        'base': '0.875rem',    // 14px
        'lg': '1rem',          // 16px
        'xl': '1.125rem',      // 18px
        '2xl': '1.5rem',       // 24px
        '3xl': '2rem',         // 32px
        '4xl': '2.5rem',       // 40px
      },
      boxShadow: {
        'glow': '0 0 20px rgba(41, 98, 255, 0.3)',
      },
    },
  },
  plugins: [],
}
