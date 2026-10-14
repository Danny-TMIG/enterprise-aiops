import { test, expect } from '@playwright/test';

test('index loads and renders asf-button', async ({ page }) => {
  await page.goto('/index.html');
  await expect(page.locator('asf-button')).toHaveCount(1);
});
