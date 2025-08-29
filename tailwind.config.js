/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './candidatures/templates/**/*.html',
    './accounts/templates/**/*.html',
    './dashboard/templates/**/*.html',
    './templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}