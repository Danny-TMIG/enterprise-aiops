import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    include: ["tests/**/*.test.ts"],
    exclude: ["tests/**/*.e2e.ts", "node_modules/**"],
  },
});
