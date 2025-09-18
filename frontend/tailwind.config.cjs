/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      spacing: { xs: '4px', sm: '8px', md: '12px', lg: '16px', xl: '24px' },
      borderRadius: { card: '1rem' },
      boxShadow: {
        card: '0 1px 2px rgba(0,0,0,.06), 0 10px 20px rgba(0,0,0,.05)'
      },
      colors: {
        'priority-low-bg': '#e2e8f0', 'priority-low-fg': '#334155',
        'priority-medium-bg': '#e0e7ff', 'priority-medium-fg': '#3730a3',
        'priority-high-bg': '#fef3c7', 'priority-high-fg': '#92400e',
        'priority-urgent-bg': '#ffe4e6', 'priority-urgent-fg': '#9f1239',
        'status-pending-bg': '#e2e8f0', 'status-pending-fg': '#334155',
        'status-done-bg': '#dcfce7', 'status-done-fg': '#166534'
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "Roboto", "Helvetica Neue", "Arial", "Noto Sans", "Liberation Sans", "sans-serif"]
      }
    },
  },
  plugins: [require('@tailwindcss/forms'), require('@tailwindcss/line-clamp')],
}

