import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      imports: ['vue', 'vue-router'],
      resolvers: [ElementPlusResolver()],
      dts: 'src/auto-imports.d.ts'
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: 'src/components.d.ts'
    })
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5000,
    allowedHosts: true,
    proxy: {
      '/api': {
        // 开发环境：使用环境变量或默认值
        // 部署时：通过 Vercel 环境变量 VITE_API_BASE 设置
        target: process.env.VITE_API_BASE || '{{RENDER_BACKEND_URL}}',
        changeOrigin: true
      },
      '/static': {
        target: process.env.VITE_API_BASE || '{{RENDER_BACKEND_URL}}',
        changeOrigin: true
      }
    }
  }
})
