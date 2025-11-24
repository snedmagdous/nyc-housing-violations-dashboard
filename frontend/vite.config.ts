/**
 * Vite Configuration
 *
 * Vite is the build tool that powers your React app.
 * Key features configured here:
 * - Path aliases: Use @ to reference src/ folder (e.g., import { api } from '@/services/api')
 * - Development server: Port 5173 with auto-open
 * - Build optimization: Code splitting and minification
 */

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],

  // Path aliases make imports cleaner
  // Instead of: import { api } from '../../services/api'
  // You can write: import { api } from '@/services/api'
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  // Development server configuration
  server: {
    port: 5173,
    open: true,  // Auto-open browser on start
    // Proxy API requests to your FastAPI backend
    // This avoids CORS issues in development
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },

  // Build optimization
  build: {
    sourcemap: true,  // Generate source maps for debugging
    rollupOptions: {
      output: {
        // Code splitting strategy
        manualChunks: {
          'vendor': ['react', 'react-dom', 'react-router-dom'],
          'charts': ['recharts'],
          'maps': ['leaflet', 'react-leaflet'],
        },
      },
    },
  },
})
