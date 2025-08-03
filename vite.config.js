import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  root: path.resolve(__dirname, 'app/static'),
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'app/static'),
    },
  },
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: path.resolve(__dirname, 'app/static/js/app.js'),
    },
  },
});

