import { test, expect } from '@playwright/test'

test.describe('Projects page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'admin')
    await page.getByRole('button', { name: /sign in/i }).click()
  })

  test('shows projects list', async ({ page }) => {
    await page.getByRole('link', { name: /projects/i }).click()
    await expect(page).toHaveURL('/projects')
    await expect(page.getByRole('heading', { name: /projects/i })).toBeVisible()
  })

  test('empty state or project cards visible', async ({ page }) => {
    await page.goto('/projects')
    const hasCards = await page.getByRole('article').count()
    const hasEmpty = await page.getByText(/no projects yet/i).isVisible().catch(() => false)
    expect(hasCards > 0 || hasEmpty).toBeTruthy()
  })
})
