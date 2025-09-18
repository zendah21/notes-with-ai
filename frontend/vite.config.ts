import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:5000',
      '/ws': {
        target: 'ws://127.0.0.1:5000',
        ws: true,
      },
    },
  },
})

