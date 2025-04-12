import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    {
      name: 'remove-use-client',
      transform(code, id) {
        if (id.includes('node_modules/@mui') || id.includes('node_modules/react-hot-toast')) {
          return {
            code: code.replace(/^['"]use client['"];?(\r\n|\r|\n)?/m, ''),
            map: null
          };
        }
      }
    }
  ],
  server: {
    port: 5175,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id: string) {
          if (id.includes('@mui/icons-material')) {
            return 'mui-icons';
          }
          if (id.includes('@mui/material')) {
            return 'mui-core';
          }
          if (['react', 'react-dom', 'react-router-dom'].some(dep => id.includes(dep))) {
            return 'vendor';
          }
        }
      }
    }
  }
});
