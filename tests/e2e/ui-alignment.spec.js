const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://demobank-e2e.selatam.harness-demo.site';

test.describe('DemoBank UI Alignment', () => {

  test('quick action cards should not be rotated', async ({ page }) => {
    await page.goto(BASE_URL);
    const cards = page.locator('.action-card');
    const count = await cards.count();
    const defects = [];

    for (let i = 0; i < count; i++) {
      const transform = await cards.nth(i).evaluate(el =>
        window.getComputedStyle(el).transform
      );
      if (transform !== 'none') {
        const label = await cards.nth(i).locator('.action-label').textContent();
        defects.push(`Card "${label.trim()}" has transform: ${transform}`);
      }
    }

    expect(defects, `Cards are rotated/displaced:\n${defects.join('\n')}`).toHaveLength(0);
  });

  test('transfer button should be visible in viewport', async ({ page }) => {
    await page.goto(`${BASE_URL}/transfer`);
    const btn = page.locator('.form-actions .btn-primary');
    const box = await btn.boundingBox();
    const viewport = page.viewportSize();

    expect(box, 'Transfer button has no bounding box').not.toBeNull();
    expect(box.x + box.width).toBeLessThan(viewport.width);
  });

});
