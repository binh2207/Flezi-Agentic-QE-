---
name: automation-framework
description: >-
  Generates Playwright POM automation under playwright-automation-framework/ using
  screen maps from live-execution as the only selector source. Produces pages, flows,
  specs, fixtures, and generation-manifest.json.
---

# Automation framework (POM generation)

Generate code **only** from screen map evidence. All paths are under `playwright-automation-framework/`.

## Prerequisites

- `support/screen-maps/<feature>.screen.json` exists (from **live-execution**; schema in `TEMPLATES.md`)
- Flow or test case input in `inputs/manual-flows/` or `inputs/test-cases/`

## Layout

```text
playwright-automation-framework/
├── tests/e2e/<feature>.spec.ts
├── tests/smoke/           (optional)
├── pages/base.page.ts
├── pages/<feature>.page.ts
├── flows/<feature>.flow.ts
├── fixtures/index.ts
├── fixtures/data/<feature>.data.json
├── support/selectors.ts   (intent keys — generated per feature)
├── support/helpers.ts     (loadScreenMap, getSelector)
├── support/screen-maps/
├── TEMPLATES.md           (copy-paste patterns)
└── reports/generation-manifest.json
```

## Rules

1. Selectors come from `getSelector(map, intent)` — never inline CSS in specs
2. Specs import `test` / `expect` from `fixtures/index.ts`
3. `waitForReady()` uses `networkidle` after navigation
4. Wait for visible landmarks before click/fill; gate sequential sections (outbound → inbound)
5. No `waitForTimeout` in generated code
6. `retries: process.env.CI ? 2 : 1` in config (already set)
7. Unmapped step targets → `RISK: no_selector_evidence` in manifest
8. `BASE_URL` must be set via `.env` before running tests

## Generation steps

1. Map each flow step `target` → screen map `intent`
2. Add `<Feature>Intents` to `support/selectors.ts` from screen map intents
3. Create `pages/<feature>.page.ts` with locators from map
4. Create `flows/<feature>.flow.ts` for reusable journey
5. Create `tests/e2e/<feature>.spec.ts` with tags from `support/test-tags.ts`
6. Remove `tests/e2e/harness-placeholder.spec.ts` once a real feature spec exists
7. Write `reports/generation-manifest.json` (shape in `TEMPLATES.md`)

## Templates

Read **only the section you need** from [playwright-automation-framework/TEMPLATES.md](../../playwright-automation-framework/TEMPLATES.md) — do not load the entire file upfront:

| Artifact to generate | Section to read |
|---|---|
| `pages/<feature>.page.ts` | `## pages/<feature>.page.ts` |
| `flows/<feature>.flow.ts` | `## flows/<feature>.flow.ts` |
| `tests/e2e/<feature>.spec.ts` | `## tests/e2e/<feature>.spec.ts` |
| `support/selectors.ts` | `## support/selectors.ts` |
| `reports/generation-manifest.json` | `## reports/generation-manifest.json` |

Existing scaffold: `pages/base.page.ts`, `support/helpers.ts`.

## Verify after generation

```bash
cd playwright-automation-framework
cp .env.example .env   # set BASE_URL
npx playwright test tests/e2e/<feature>.spec.ts
```

Update manifest `verification` with command and pass/fail counts.
