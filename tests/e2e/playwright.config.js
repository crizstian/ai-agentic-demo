const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: '.',
  timeout: 30000,
  retries: 0,
  use: {
    baseURL: process.env.BASE_URL || 'http://demobank-e2e.selatam.harness-demo.site',
    headless: true,
    screenshot: 'only-on-failure',
  },
  reporter: [['json', { outputFile: '/tmp/pw-results.json' }]],
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
  ],
});
