import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "tests",
  testMatch: "**/*.e2e.ts",
  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
  ],
  webServer: {
    command: "npm run dev",
    port: 5173,
    reuseExistingServer: true,
  },
});
