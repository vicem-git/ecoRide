import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  root: 'app/static',
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'app/static'),
    },
  },
  build: {
    outDir: path.resolve(__dirname, 'dist'),
    rollupOptions: {
      input: path.resolve(__dirname, 'app/static/js/app.js'),
    },
  },
});

