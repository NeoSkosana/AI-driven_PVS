import { test, expect } from '@playwright/test';

test.describe('Problem Validation Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('[data-testid="username"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'testpassword');
    await page.click('[data-testid="login-button"]');
  });

  test('should submit a problem statement and show validation results', async ({ page }) => {
    await page.goto('/problem-form');
    
    // Fill in problem statement form
    await page.fill('[data-testid="title"]', 'AI-Powered Personal Finance App for Gen Z');
    await page.fill('[data-testid="description"]', 'A mobile app that uses AI to help Gen Z manage their finances better, providing personalized advice and automated savings features.');
    await page.fill('[data-testid="keywords"]', 'fintech, Gen Z, personal finance');
    await page.fill('[data-testid="target-audience"]', 'Generation Z (ages 18-25)');
    await page.fill('[data-testid="industry"]', 'Fintech');
    
    // Submit form
    await page.click('[data-testid="submit-button"]');
    
    // Check for submission confirmation
    const confirmationMessage = await page.locator('[data-testid="confirmation-message"]');
    await expect(confirmationMessage).toBeVisible();
    
    // Wait for results to be processed
    await page.waitForSelector('[data-testid="validation-results"]', { timeout: 30000 });
    
    // Verify results components are present
    await expect(page.locator('[data-testid="sentiment-score"]')).toBeVisible();
    await expect(page.locator('[data-testid="market-validation"]')).toBeVisible();
    await expect(page.locator('[data-testid="recommendations"]')).toBeVisible();
  });

  test('should show validation history in dashboard', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Check for validation history table
    const historyTable = await page.locator('[data-testid="validation-history"]');
    await expect(historyTable).toBeVisible();
    
    // Click on a validation result
    await page.click('[data-testid="validation-result-link"]');
    
    // Verify detailed results page
    await expect(page.locator('[data-testid="validation-details"]')).toBeVisible();
  });

  test('should handle form validation errors', async ({ page }) => {
    await page.goto('/problem-form');
    
    // Try to submit empty form
    await page.click('[data-testid="submit-button"]');
    
    // Check for validation error messages
    const errorMessages = await page.locator('[data-testid="validation-error"]');
    await expect(errorMessages).toHaveCount(5); // One for each required field
    
    // Fill one field and verify remaining errors
    await page.fill('[data-testid="title"]', 'Test Title');
    await expect(errorMessages).toHaveCount(4);
  });
});
