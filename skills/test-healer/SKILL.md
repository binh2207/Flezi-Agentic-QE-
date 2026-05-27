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

## Minimal context protocol (read in order, stop when enough)

Load only what the current attempt needs — do not read the full report or full screen map upfront:

1. **Read stderr / test title only** — classify the error type from the failure message alone.
2. **If selector error:** read only the `elements` array of the screen map for the failing intent. Do not load the full map if the intent key is already known.
3. **If timeout/navigation error:** read only the last 20 lines of the HTML report stderr section. Do not load trace zip unless steps 1–2 are inconclusive after attempt 1.
4. **Load trace zip only on attempt 3** if prior attempts did not resolve the failure.

## Loop (max 3 attempts per failure)

1. Classify: timeout / strict mode / not found / navigation / env blocker
2. Apply **one** change set:
   - Update selector from screen map `intent` (read only that element entry)
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
