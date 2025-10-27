import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { resolve } from 'node:path';

const testConfig = {
  environment: 'jsdom',
  globals: true,
  globalSetup: './tests/globalSetup.ts',
  setupFiles: ['./tests/setup.ts'],
  pool: 'threads',
  poolOptions: {
    threads: {
      singleThread: true,
    },
  },
  deps: {
    inline: ['whatwg-url', 'webidl-conversions'],
  },
  coverage: {
    provider: 'v8',
    reporter: ['text', 'json', 'html'],
    exclude: [
      'node_modules/',
      'tests/',
      '**/*.d.ts',
      '**/*.config.*',
      '**/mockData',
      '**/.next',
    ],
  },
} satisfies Parameters<typeof defineConfig>[0]['test'];

export default defineConfig({
  plugins: [react()],
  test: testConfig,
  resolve: {
    alias: {
      '@': resolve(__dirname, './'),
      'whatwg-url': resolve(__dirname, './tests/__mocks__/whatwg-url.ts'),
      'webidl-conversions': resolve(__dirname, './tests/__mocks__/webidl-conversions.ts'),
    },
  },
});
