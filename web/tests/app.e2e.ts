import { test, expect } from "@playwright/test";

test("asf-app renders the fabric status", async ({ page }) => {
  await page.route("**/status.json", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        tree: { components_total: 150 },
        tracked: { tracked_files: 3174 },
        verdict: { status: "OK" },
      }),
    });
  });

  await page.goto("/");
  await expect(page.locator("h1")).toHaveText("Aether Sovereign Fabric");
  await expect(page.locator(".status .ok")).toContainText("verdict: OK");
  await expect(page.locator(".status")).toContainText("components_total: 150");
});
