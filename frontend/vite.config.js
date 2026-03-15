import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/dashboard/',
  build: {
    outDir: 'dist'
  },
  server: {
    proxy: {
      '/api': 'http://localhost',
      '/ws': { target: 'ws://localhost', ws: true, changeOrigin: true }
    }
  }
})
