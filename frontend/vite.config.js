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
    outDir: path.resolve(__dirname, '../flask_app/app/static/dist'),
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: path.resolve(__dirname, 'js/app.js'),
    },
  },
});

