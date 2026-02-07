/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#00E676',
          dark: '#00C853',
          light: '#69F0AE',
        },
        dark: {
          DEFAULT: '#1A2332',
          light: '#2D3748',
        }
      }
    },
  },
  plugins: [],
}
