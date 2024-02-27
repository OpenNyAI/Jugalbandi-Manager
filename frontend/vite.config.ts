import { defineConfig } from 'vite';
import path from 'path';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  publicDir: path.resolve(__dirname, 'public'),
  preview: {
    port: 4173,
    strictPort: true,
  },
  server: {
    port: 4173,
    strictPort: true,
    host: true,
    origin: 'http://0.0.0.0:4173',
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  }
});
