import { fileURLToPath, URL } from 'node:url'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // 加载环境变量（使用当前工作目录）
  // @ts-ignore - process 在 Node.js 环境中可用
  const env = loadEnv(mode, process.cwd(), '')
  
  // 开发环境下输出代理配置信息
  if (mode === 'development') {
    console.log('Vite 代理配置:')
    console.log('- DOCKER_ENV:', env.DOCKER_ENV)
    console.log('- API 代理目标:', env.DOCKER_ENV === 'true' ? 'http://backend:8000' : 'http://localhost:8000')
  }
  
  return {
    plugins: [
      vue(),
      vueJsx(),
      AutoImport({
        resolvers: [ElementPlusResolver()],
      }),
      Components({
        resolvers: [ElementPlusResolver()],
      }),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      host: '0.0.0.0',
      port: 5173,
      // API 代理配置
      // 在 Docker 环境中，通过服务名访问后端；本地开发时使用 localhost
      proxy: {
        '/api': {
          target: env.DOCKER_ENV === 'true' 
            ? 'http://backend:8000' 
            : 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path, // 保持路径不变
          // 确保错误响应也被正确转发
          configure: (proxy, _options) => {
            proxy.on('error', (err, _req, res) => {
              console.error('代理错误:', err)
            })
            proxy.on('proxyRes', (proxyRes, req, res) => {
              // 开发环境下记录代理响应信息
              if (mode === 'development' && req.url?.includes('/auth/login')) {
                console.log('代理响应:', {
                  statusCode: proxyRes.statusCode,
                  headers: proxyRes.headers,
                  url: req.url
                })
              }
            })
          }
        }
      }
    }
  }
})

