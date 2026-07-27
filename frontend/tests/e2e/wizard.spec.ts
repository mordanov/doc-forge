import { test, expect } from '@playwright/test'

test.describe('New Project wizard happy path', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
  })

  test('login then reach wizard step 1', async ({ page }) => {
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'admin')
    await page.getByRole('button', { name: /sign in/i }).click()

    await expect(page).toHaveURL('/')
    await page.getByRole('link', { name: /new project/i }).click()
    await expect(page).toHaveURL('/new-project')

    await expect(page.getByText('Upload')).toBeVisible()
    await expect(page.getByRole('button', { name: /back/i })).toBeVisible()
  })

  test('upload area renders', async ({ page }) => {
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'admin')
    await page.getByRole('button', { name: /sign in/i }).click()
    await page.goto('/new-project')

    await expect(page.getByRole('button', { name: /upload document/i })).toBeVisible()
  })
})
