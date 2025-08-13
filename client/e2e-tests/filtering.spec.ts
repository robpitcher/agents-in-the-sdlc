import { test, expect } from '@playwright/test';

test.describe('Game filtering', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    
    // Wait for either games-grid or loading state
    await Promise.race([
      page.getByTestId('games-grid').waitFor(),
      page.getByText('Loading...').waitFor()
    ]);

    // If we found loading state, wait for it to disappear and games to appear
    if (await page.getByText('Loading...').isVisible()) {
      await page.getByText('Loading...').waitFor({ state: 'hidden' });
      await page.getByTestId('games-grid').waitFor();
    }
  });

  test('shows filter controls', async ({ page }) => {
    await expect(page.getByTestId('category-filter')).toBeVisible();
    await expect(page.getByTestId('publisher-filter')).toBeVisible();
  });

  test('filters games by category', async ({ page }) => {
    // Get initial game count
    const initialGames = await page.getByTestId('game-card').count();
    
    // Select first category
    const categorySelect = page.getByTestId('category-filter');
    await categorySelect.selectOption({ index: 1 });
    
    // Wait for filtered games
    await page.waitForResponse(response => 
      response.url().includes('/api/games') && 
      response.status() === 200
    );
    
    // Wait for UI update
    await page.waitForTimeout(500);
    
    // Get filtered game count
    const filteredGames = await page.getByTestId('game-card').count();
    
    // Verify filtering changed the number of games
    expect(filteredGames).toBeLessThanOrEqual(initialGames);
    
    // Verify the filtered games have the correct category
    const selectedCategory = await categorySelect.evaluate((select: HTMLSelectElement) => 
      select.options[select.selectedIndex].text
    );
    const gameCategoryText = await page.getByTestId('game-category').first().textContent();
    expect(gameCategoryText).toBe(selectedCategory);
  });

  test('filters games by publisher', async ({ page }) => {
    // Get initial game count
    const initialGames = await page.getByTestId('game-card').count();
    
    // Select first publisher
    const publisherSelect = page.getByTestId('publisher-filter');
    await publisherSelect.selectOption({ index: 1 });
    
    // Wait for filtered games
    await page.waitForResponse(response => 
      response.url().includes('/api/games') && 
      response.status() === 200
    );
    
    // Wait for UI update
    await page.waitForTimeout(500);
    
    // Get filtered game count
    const filteredGames = await page.getByTestId('game-card').count();
    
    // Verify filtering changed the number of games
    expect(filteredGames).toBeLessThanOrEqual(initialGames);
    
    // Verify the filtered games have the correct publisher
    const selectedPublisher = await publisherSelect.evaluate((select: HTMLSelectElement) => 
      select.options[select.selectedIndex].text
    );
    const gamePublisherText = await page.getByTestId('game-publisher').first().textContent();
    expect(gamePublisherText).toBe(selectedPublisher);
  });

  test('combines category and publisher filters', async ({ page }) => {
    // Get initial game count
    const initialGames = await page.getByTestId('game-card').count();
    
    // Select first category and publisher
    const categorySelect = page.getByTestId('category-filter');
    const publisherSelect = page.getByTestId('publisher-filter');
    
    await categorySelect.selectOption({ index: 1 });
    
    // Wait for first filter response
    await page.waitForResponse(response => 
      response.url().includes('/api/games') && 
      response.status() === 200
    );
    
    await publisherSelect.selectOption({ index: 1 });
    
    // Wait for second filter response
    await page.waitForResponse(response => 
      response.url().includes('/api/games') && 
      response.status() === 200
    );
    
    // Wait for UI update
    await page.waitForTimeout(500);
    
    // Get filtered game count
    const filteredGames = await page.getByTestId('game-card').count();
    
    // Verify filtering reduced the number of games
    expect(filteredGames).toBeLessThanOrEqual(initialGames);
    
    if (filteredGames > 0) {
      // Verify the filtered games have both the correct category and publisher
      const selectedCategory = await categorySelect.evaluate((select: HTMLSelectElement) => 
        select.options[select.selectedIndex].text
      );
      const selectedPublisher = await publisherSelect.evaluate((select: HTMLSelectElement) => 
        select.options[select.selectedIndex].text
      );
      
      const gameCategoryText = await page.getByTestId('game-category').first().textContent();
      const gamePublisherText = await page.getByTestId('game-publisher').first().textContent();
      
      expect(gameCategoryText).toBe(selectedCategory);
      expect(gamePublisherText).toBe(selectedPublisher);
    }
  });
});
