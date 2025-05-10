import { test as base, Page, expect } from '@playwright/test';

type CustomFixtures = {
    loggedInPage: Page;
};

// Extend base test fixture with custom utilities
export const test = base.extend<CustomFixtures>({
    // Add a logged in page fixture
    loggedInPage: async ({ page }, use) => {
        await page.goto('/login');
        await page.fill('[data-testid="username"]', 'test@example.com');
        await page.fill('[data-testid="password"]', 'testpassword');
        await page.click('[data-testid="login-button"]');
        await expect(page).toHaveURL(/.*dashboard/);
        await use(page);
    },
});

export { expect };

// Helper functions for common test operations
export async function submitProblemStatement(page: Page, data: {
    title: string;
    description: string;
    keywords: string;
    targetAudience: string;
    industry: string;
}) {
    await page.goto('/problem-form');
    await page.fill('[data-testid="title"]', data.title);
    await page.fill('[data-testid="description"]', data.description);
    await page.fill('[data-testid="keywords"]', data.keywords);
    await page.fill('[data-testid="target-audience"]', data.targetAudience);
    await page.fill('[data-testid="industry"]', data.industry);
    await page.click('[data-testid="submit-button"]');
}

export async function validateSuccessfulSubmission(page: Page) {
    const confirmationMessage = await page.locator('[data-testid="confirmation-message"]');
    await expect(confirmationMessage).toBeVisible();
    await page.waitForSelector('[data-testid="validation-results"]', { timeout: 30000 });
}

export const mockProblemStatement = {
    title: 'AI-Powered Personal Finance App for Gen Z',
    description: 'A mobile app that uses AI to help Gen Z manage their finances better, providing personalized advice and automated savings features.',
    keywords: 'fintech, Gen Z, personal finance',
    targetAudience: 'Generation Z (ages 18-25)',
    industry: 'Fintech'
};
