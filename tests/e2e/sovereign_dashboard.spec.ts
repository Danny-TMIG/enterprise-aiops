import { test, expect } from '@playwright/test';

test.describe('Aether Sovereign PWA Dashboard', () => {
  test('loads control plane and displays live node metrics', async ({ page }) => {
    await page.goto('http://127.0.0.1:8000/dashboard.html');

    await expect(page.locator('h1')).toContainText('Aether Sovereign Fabric');

    const statusBadge = page.locator('#node-status');
    await expect(statusBadge).toBeVisible();

    const wsLog = page.locator('#ws-connection-log');
    await expect(wsLog).toContainText('Connected');
  });

  test('submits cognitive query and renders response', async ({ page }) => {
    await page.goto('http://127.0.0.1:8000/dashboard.html');

    await page.fill('#prompt-input', 'Verify system RAM integrity and node attestation.');
    await page.click('#submit-infer-btn');

    const responseBox = page.locator('#inference-output');
    await expect(responseBox).not.toBeEmpty({ timeout: 10000 });
  });
});
