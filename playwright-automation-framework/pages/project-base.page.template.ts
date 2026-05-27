/**
 * Project base page — copy to pages/<project>-base.page.ts
 * Extend this class (not BasePage directly) for all feature pages in your project.
 * Add project-specific component helpers here.
 */
import { Page } from '@playwright/test';
import { BasePage } from './base.page';

export class ProjectBasePage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // -- Date picker ----------------------------------------------------------
  // Usage: await this.fillDatePicker('[data-testid="start-date"]', '2024-06-15')
  async fillDatePicker(selector: string, dateStr: string) {
    await this.page.locator(selector).click();
    await this.page.locator('[class*="calendar"]').waitFor({ state: 'visible' });
    // Navigate to correct month if needed, then click target day
    const [year, month, day] = dateStr.split('-').map(Number);
    // Simplified: type directly if input accepts ISO format
    await this.page.locator(selector).fill(dateStr);
    await this.page.keyboard.press('Escape');
  }

  // -- File upload ----------------------------------------------------------
  // Usage: await this.uploadFile('[data-testid="upload-input"]', './fixtures/data/sample.pdf')
  async uploadFile(selector: string, filePath: string) {
    const input = this.page.locator(selector);
    await input.waitFor({ state: 'attached' });
    await input.setInputFiles(filePath);
  }

  // -- Rich text editor (Quill / TipTap) ------------------------------------
  // Usage: await this.typeInEditor('[data-testid="description-editor"]', 'Hello world')
  async typeInEditor(selector: string, text: string) {
    const editor = this.page.locator(selector).locator('.ql-editor, [contenteditable="true"]').first();
    await editor.waitFor({ state: 'visible' });
    await editor.click();
    await editor.fill(text);
  }

  // -- Toast / notification -------------------------------------------------
  // Usage: await this.waitForToast('Saved successfully')
  async waitForToast(expectedText: string, timeoutMs = 5000) {
    await this.page
      .locator('[role="alert"], [data-testid="toast"]')
      .filter({ hasText: expectedText })
      .waitFor({ state: 'visible', timeout: timeoutMs });
  }

  // -- Multi-select dropdown (react-select) ----------------------------------
  // Usage: await this.selectOption('[data-testid="tags-select"]', 'Option label')
  async selectOption(containerSelector: string, optionText: string) {
    await this.page.locator(containerSelector).click();
    await this.page.locator('[class*="menu"]').waitFor({ state: 'visible' });
    await this.page.locator('[class*="option"]').filter({ hasText: optionText }).click();
  }

  // -- Add project-specific helpers below -----------------------------------
}
