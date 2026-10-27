import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { defineConfig, loadEnv } from 'vite'
import mkcert from 'vite-plugin-mkcert'

export default defineConfig(({ command, mode, isPreview }) => {
  if (command !== 'serve' || isPreview) {
    return { plugins: [vue(), tailwindcss()] }
  }

  // Dev server: https with a locally trusted certificate, so Telegram Desktop can open it as a Mini
  // App, and the API proxied on the same origin (no CORS, no mixed content).
  const { VITE_API_BASE_URL } = loadEnv(mode, process.cwd())
  return {
    plugins: [vue(), tailwindcss(), mkcert()],
    define: { 'import.meta.env.VITE_API_BASE_URL': JSON.stringify('') },
    server: {
      // IPv4 loopback: Node binds `localhost` to ::1 only on macOS, so https://127.0.0.1:5173 would
      // refuse connections. https://localhost:5173 still works, as localhost resolves to 127.0.0.1 too.
      host: '127.0.0.1',
      proxy: { '/api': { target: VITE_API_BASE_URL, changeOrigin: true } },
    },
  }
})
