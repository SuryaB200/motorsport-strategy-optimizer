/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        pit: {
          black: '#090D12',
          sidebar: '#0D1219',
          card: '#111821',
          panel: '#151D27',
          border: '#28313D',
          muted: '#7E8B9B',
          red: '#F20D2F',
          redHover: '#D90B2A',
          green: '#16B86A',
          yellow: '#F5C928',
          blue: '#1677E8',
          cyan: '#06B6D4',
          orange: '#F97316',
        },
        compound: {
          soft: '#EF4444',
          medium: '#F59E0B',
          hard: '#E2E8F0',
          inter: '#10B981',
          wet: '#3B82F6',
        }
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        display: ['"Space Grotesk"', 'sans-serif'],
      },
      boxShadow: {
        'f1-glow': '0 0 15px rgba(242, 13, 47, 0.25)',
        'f1-card': '0 4px 20px -2px rgba(0, 0, 0, 0.5)',
      }
    },
  },
  plugins: [],
}

