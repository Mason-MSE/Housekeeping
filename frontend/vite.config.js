import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// Vite configuration for the frontend application
export default defineConfig({ 
  // Vue plugin for SFC support
  plugins: [vue()], 
  // Path alias: @ maps to src/
  resolve: { alias: { '@': path.resolve(__dirname, 'src') } },
  // Dev server configuration with API proxy
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '/docs': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path
      },
      '/openapi.json': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '/redoc': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
}) 
