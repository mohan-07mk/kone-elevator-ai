import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const targetApi = env.VITE_API_URL || 'https://kone-elevator-ai-production.up.railway.app';
  const targetWs = env.VITE_WS_URL || 'wss://kone-elevator-ai-production.up.railway.app';

  return {
    plugins: [react()],
    server: {
      host: '0.0.0.0',
      port: 3000,
      proxy: {
        '/api': {
          target: targetApi,
          changeOrigin: true,
          secure: false,
        },
        '/ws': {
          target: targetWs,
          ws: true,
          secure: false,
        },
      },
    },
  };
});

