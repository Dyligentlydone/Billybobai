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
  base: '/',
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html')
      },
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          'mui-core': ['@mui/material'],
          'mui-icons': ['@mui/icons-material']
        }
      }
    }
  }
});
