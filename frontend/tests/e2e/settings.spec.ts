import { test, expect } from '@playwright/test'

test.describe('Settings dark mode', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'admin')
    await page.getByRole('button', { name: /sign in/i }).click()
  })

  test('settings page is accessible', async ({ page }) => {
    await page.getByRole('link', { name: /settings/i }).click()
    await expect(page).toHaveURL('/settings')
    await expect(page.getByRole('heading', { name: /settings/i })).toBeVisible()
  })

  test('dark mode toggle changes html class', async ({ page }) => {
    await page.goto('/settings')
    const toggle = page.getByRole('switch', { name: /dark mode/i })
    const isDark = await page.evaluate(() => document.documentElement.classList.contains('dark'))
    await toggle.click()
    const isNowDark = await page.evaluate(() => document.documentElement.classList.contains('dark'))
    expect(isNowDark).toBe(!isDark)
  })
})
