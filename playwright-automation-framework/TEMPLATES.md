# Harness templates

Replace `<Feature>`, `<feature>`, and intent placeholders using **screen map evidence only**.

## `support/screen-maps/<feature>.screen.json`

Produced by **live-execution** before any POM code is written.

```json
{
  "page": "<document.title>",
  "url": "https://example.com/path",
  "route": "/path",
  "build_id": null,
  "dom_fingerprint": "<sha256 of sorted element fingerprints>",
  "freshness": {
    "status": "FRESH",
    "checked_at": "<ISO8601>",
    "dom_drift_ratio": 0,
    "max_allowed_drift_ratio": 0.2,
    "max_age_hours": 168
  },
  "captured_at": "<ISO8601>",
  "element_count": 1,
  "elements": [
    {
      "intent": "submit_button",
      "selector": "[data-testid=\"submit\"]",
      "tag": "button",
      "type": "button",
      "label": null,
      "text": "Submit",
      "placeholder": null,
      "visible": true,
      "stability": "data-attribute"
    }
  ]
}
```

Rules:

- `intent` — unique snake_case key; copied into `support/selectors.ts`
- `selector` — from live DOM only; prefer `data-testid` / `data-qa` / `aria-label` / `id`
- `stability` — `data-attribute` | `aria` | `id` | `css` (flag `css` as `RISK` in manifest)
- Rename auto-generated intents (e.g. from raw labels) to meaningful names before POM generation

---

## `support/selectors.ts` (per feature)

```typescript
export const <Feature>Intents = {
  submitBtn: 'submit_button', // must match screen map elements[].intent
} as const;
```

## `pages/<feature>.page.ts`

```typescript
import { Page } from '@playwright/test';
import { BasePage } from './base.page';
import { loadScreenMap, getSelector } from '../support/helpers';
import { <Feature>Intents } from '../support/selectors';

export class <Feature>Page extends BasePage {
  private map = loadScreenMap('<feature>');

  readonly submitBtn = this.page.locator(
    getSelector(this.map, <Feature>Intents.submitBtn),
  );

  constructor(page: Page) {
    super(page);
  }

  async submit() {
    await this.submitBtn.waitFor({ state: 'visible' });
    await this.submitBtn.click();
  }
}
```

## `flows/<feature>.flow.ts`

```typescript
import { Page } from '@playwright/test';
import { <Feature>Page } from '../pages/<feature>.page';

export async function <feature>Flow(page: Page, data: { value: string }) {
  const p = new <Feature>Page(page);
  await p.navigate('/<path-from-screen-map>');
  await p.submit();
}
```

## `fixtures/data/<feature>.data.json`

```json
{
  "valid": { "value": "<from-flow-input>" },
  "invalid": { "value": "<edge-case>" }
}
```

## `tests/e2e/<feature>.spec.ts`

```typescript
import { expect, test } from '../../fixtures';
import { Tags } from '../../support/test-tags';
import { <feature>Flow } from '../../flows/<feature>.flow';
import data from '../../fixtures/data/<feature>.data.json';

test.describe('<Feature>', () => {
  test('happy path @regression', { tag: Tags.regression }, async ({ page }) => {
    await <feature>Flow(page, data.valid);
    await expect(page).toHaveURL(/expected-route/);
  });
});
```

## `reports/generation-manifest.json`

```json
{
  "feature": "<feature>",
  "generated_at": "<ISO8601>",
  "status": "ready",
  "screen_map": "support/screen-maps/<feature>.screen.json",
  "artifacts": [
    "support/selectors.ts",
    "pages/<feature>.page.ts",
    "flows/<feature>.flow.ts",
    "tests/e2e/<feature>.spec.ts"
  ],
  "risks": [],
  "verification": {
    "command": "npx playwright test tests/e2e/<feature>.spec.ts",
    "passed": 0,
    "failed": 0
  }
}
```
