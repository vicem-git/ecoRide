import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite'
import path from 'path';

export default defineConfig({
  root: '.',
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'app/static'),
    },
  },
  plugins: [
    tailwindcss(),
  ],
  build: {
    outDir: 'app/static/dist',
    rollupOptions: {
      input: path.resolve(__dirname, 'app/static/js/app.js'),
    },
  },
});

