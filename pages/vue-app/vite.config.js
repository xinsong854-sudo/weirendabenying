import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    target: 'es2022',
    outDir: '../dist',
    emptyOutDir: true,
    sourcemap: false,
    cssCodeSplit: true,
    minify: 'esbuild',
    assetsInlineLimit: 2048,
    rollupOptions: {
      output: {
        manualChunks: undefined,
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash][extname]'
      }
    }
  },
  esbuild: {
    legalComments: 'none',
    drop: ['debugger'],
    pure: ['console.log', 'console.debug', 'console.info']
  }
})
