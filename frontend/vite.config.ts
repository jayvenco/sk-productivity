import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    port: 4443,
    proxy: {
      '/api': 'http://localhost:4442',
    },
  },
});