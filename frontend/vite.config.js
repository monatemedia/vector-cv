import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: '/',
  server: {
    proxy: {
      // Shims the /api calls to the backend during local development
      '/api': {
        target: 'http://localhost:8010',
        changeOrigin: true,
      },
    }
  }
})