import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('should show login error with invalid credentials', async ({ page }) => {
    await page.goto('/login');
    
    // Fill in invalid credentials
    await page.fill('[data-testid="username"]', 'invalid@example.com');
    await page.fill('[data-testid="password"]', 'wrongpassword');
    await page.click('[data-testid="login-button"]');
    
    // Check for error message
    const errorMessage = await page.locator('[data-testid="error-message"]');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toContainText('Invalid credentials');
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    await page.goto('/login');
    
    // Fill in valid credentials
    await page.fill('[data-testid="username"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'testpassword');
    await page.click('[data-testid="login-button"]');
    
    // Check that we're redirected to the dashboard
    await expect(page).toHaveURL(/.*dashboard/);
    
    // Verify navbar shows user info
    const userInfo = await page.locator('[data-testid="user-info"]');
    await expect(userInfo).toBeVisible();
  });

  test('should logout successfully', async ({ page }) => {
    // First login
    await page.goto('/login');
    await page.fill('[data-testid="username"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'testpassword');
    await page.click('[data-testid="login-button"]');
    
    // Click logout button
    await page.click('[data-testid="logout-button"]');
    
    // Verify we're redirected to login page
    await expect(page).toHaveURL(/.*login/);
    
    // Verify protected routes are no longer accessible
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/.*login/);
  });
});
