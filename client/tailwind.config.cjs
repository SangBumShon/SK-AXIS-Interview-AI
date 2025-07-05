/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'sk-red': '#E60012',
        'sk-orange': '#FF7A00',
      },
      borderRadius: {
        'button': '0.5rem',
      }
    },
  },
  plugins: [],
} 