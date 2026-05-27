---
name: test-healer
description: >-
  Repairs failing Playwright tests in playwright-automation-framework/ using traces,
  error context, and screen maps. Minimal diffs to locators and waits only.
---

# Playwright self-healing

Fix **automation scaffolding**, not product behavior.

## Scope

- Directory: `playwright-automation-framework/`
- Evidence: stderr, HTML report, `reports/test-results/`, trace zip, screen maps

## Loop (max 3 attempts per failure)

1. Classify: timeout / strict mode / not found / navigation / env blocker
2. Apply **one** change set:
   - Update selector from fresh screen map `intent`
   - Add `waitFor({ state: 'visible' })` or section gate
   - Narrow locator scope (container)
3. Re-run narrowly:

```bash
cd playwright-automation-framework
# ensure .env exists with BASE_URL
npx playwright test tests/e2e/<feature>.spec.ts --grep "<title fragment>"
```

4. Record selector changes without map backing as `RISK: heuristic_selector`

## Forbidden without user approval

- Removing assertions
- `test.skip` / empty tests to force green
- Bypassing CAPTCHA or production payment

## Escalation

After 3 failures: report blocker, recommend live-execution recapture or human env fix.
