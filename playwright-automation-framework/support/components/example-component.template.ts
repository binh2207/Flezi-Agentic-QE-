/**
 * Template for a custom component helper.
 * Copy to support/components/<your-component>.ts and adapt.
 *
 * Pattern: pure functions receiving (page, selector, ...args)
 * — no class state, no imports from core files.
 */
import { Page } from '@playwright/test';

/**
 * Interact with <YourComponent>.
 * Document the component in inputs/project-config/custom-components.md.
 */
export async function interactWithComponent(
  page: Page,
  selector: string,
  value: string,
): Promise<void> {
  const component = page.locator(selector);
  await component.waitFor({ state: 'visible' });

  // Step 1: open / activate component
  await component.click();

  // Step 2: wait for inner panel / dropdown / popup
  const panel = page.locator('[data-testid="component-panel"]');
  await panel.waitFor({ state: 'visible' });

  // Step 3: perform interaction
  await panel.locator('[data-value]').filter({ hasText: value }).click();

  // Step 4: wait for panel to close and state to settle
  await panel.waitFor({ state: 'hidden' });
}

/**
 * Assert component displays the expected value.
 */
export async function expectComponentValue(
  page: Page,
  selector: string,
  expectedValue: string,
): Promise<void> {
  const component = page.locator(selector);
  await component.waitFor({ state: 'visible' });
  // Adapt the inner selector to your component's DOM structure
  await component.locator('[data-selected]').filter({ hasText: expectedValue }).waitFor({ state: 'visible' });
}
