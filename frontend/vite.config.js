import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite'
import path from 'path';

export default defineConfig({
  root: '.',
  resolve: {
    alias: {
      '@': path.resolve(__dirname),
    },
  },
  plugins: [
    tailwindcss(),
  ],
  build: {
    outDir: 'flask_app/static/dist',
    rollupOptions: {
      input: path.resolve(__dirname, 'js/app.js'),
    },
  },
});

