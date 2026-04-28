import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { powerApps } from '@microsoft/power-apps-vite';

export default defineConfig({
  plugins: [react(), tailwindcss(), powerApps()],
  server: { port: 3000 },
});
