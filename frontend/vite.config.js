const { defineConfig } = require('vite');
const vue = require('@vitejs/plugin-vue');
const path = require('path');

// https://vitejs.dev/config/
module.exports = defineConfig(async () => {
  const frappeui = (await import('frappe-ui/vite/index.js')).default;
  const Icons = (await import('unplugin-icons/vite')).default;

  return {
    plugins: [
      frappeui({
        indexHtmlPath: path.resolve(__dirname, '../education/www/student-portal.html'),
      }),
      vue(),
      Icons({
        compiler: 'vue3',
      }),
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
    },
    build: {
      outDir: `../${path.basename(path.resolve('..'))}/public/frontend`,
      emptyOutDir: true,
      target: 'es2020',
      rollupOptions: {
        output: {
          manualChunks: {
            'frappe-ui': ['frappe-ui'],
          },
        },
      },
    },
    optimizeDeps: {
      include: ['feather-icons', 'showdown', 'engine.io-client'],
    },
  };
});

