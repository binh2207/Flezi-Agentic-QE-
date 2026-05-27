---
name: pipeline-orchestrator
description: >-
  AI harness engineering for Playwright — live MCP execution captures screen maps,
  automation-framework generates POM tests from evidence, test-healer repairs drift.
  Use for end-to-end harness work, new feature automation, or fixing flaky/failing specs.
---

# Harness Engineering (Playwright + AI)

Transform manual flows or test cases into **evidence-backed** Playwright automation. All generated code lives under `playwright-automation-framework/`.

## When to use

- Build or extend Playwright POM automation from a URL + flow description
- Capture screen maps before writing selectors
- Generate specs/pages/flows from execution evidence
- Heal failing tests after selector or timing drift
- Run the full harness pipeline in one session

## Inputs

| Input | Required | Example |
|-------|----------|---------|
| Feature name (slug) | Yes | `checkout` (your feature id) |
| Target URL or `BASE_URL` | Yes | From `playwright-automation-framework/.env` |
| Flow description | Yes | `inputs/manual-flows/<feature>.md` or test cases MD |
| JIRA key | No | `PROJ-123` (only if reporting) |

## Pipeline

```
inputs (manual flow / test cases)
        │
        ▼
┌───────────────────────┐
│ 1. live-execution     │  MCP Playwright → screen maps + execution report
│    (evidence)         │  support/screen-maps/<feature>.screen.json
└───────────────────────┘
        │
        ▼
┌───────────────────────┐
│ 2. automation-framework│  POM: pages/, flows/, tests/e2e/
│    (generation)       │  reports/generation-manifest.json
└───────────────────────┘
        │
        ▼
┌───────────────────────┐
│ 3. verify             │  cd playwright-automation-framework && npx playwright test
└───────────────────────┘
        │
        ▼ (on failure)
┌───────────────────────┐
│ 4. test-healer             │  minimal locator/wait fixes, re-run (≤3 attempts)
└───────────────────────┘
        │
        ▼ (optional)
┌───────────────────────┐
│ 5. test-jira-reporter │  post QA report to JIRA
└───────────────────────┘
```

## Step 1 — Live execution

> Read `skills/live-execution/SKILL.md` now — only this file, no others yet.

- Navigate with MCP Playwright (project `playwright` via `npm run setup:mcp`, or `plugin-playwright-playwright` / `cursor-ide-browser`)
- Capture screen maps **before** interacting on each unique route/modal
- Write maps to `playwright-automation-framework/support/screen-maps/<feature>.screen.json`
- Produce an execution report under `playwright-automation-framework/reports/`

**Gate:** Do not proceed to Step 2 without at least one screen map for the primary route.

## Step 2 — Automation generation

> Read `skills/automation-framework/SKILL.md` now — only this file.

- Use screen map `elements[].selector` only — never invent selectors
- Output under `playwright-automation-framework/` only
- Write `reports/generation-manifest.json` listing artifacts and any `RISK:` flags

## Step 3 — Verify

```bash
cd playwright-automation-framework
npm install
npx playwright install chromium
cp .env.example .env   # set BASE_URL (loaded automatically via dotenv)
npx playwright test tests/e2e/<feature>.spec.ts
```

`playwright.config.ts` loads `.env` from this directory. Until feature specs exist, `npm test` runs the smoke placeholder (skipped).

Record pass/fail counts in the generation manifest. If all tests pass, skip Step 4.

## Step 4 — Self-healing (only if Step 3 has failures)

> Read `skills/test-healer/SKILL.md` now — skip entirely if Step 3 passed.

- Max 3 patch attempts per failure cluster
- Prefer screen map updates over heuristic CSS
- Never weaken product assertions without explicit user approval

## Step 5 — JIRA (only if ticket key provided)

> Read `skills/test-jira-reporter/SKILL.md` now — skip if no JIRA key was given.

## Final report

```
╔══════════════════════════════════════════════════════╗
║  HARNESS ENGINEERING COMPLETE                        ║
╚══════════════════════════════════════════════════════╝

Feature:     <feature>
Screen map:  playwright-automation-framework/support/screen-maps/<feature>.screen.json
Automation:  pages/, flows/, tests/e2e/<feature>.spec.ts
Manifest:    reports/generation-manifest.json
Verification: N passed / M failed
Risks:       (list RISK flags or "none")
```

## Error handling

| Situation | Action |
|-----------|--------|
| No screen map | Run live-execution capture first |
| CAPTCHA / hard auth | Stop; document blocker for human |
| STALE_HARD screen map | Recapture before generation |
| All tests pass | Skip self-healing |
| Selector not in map | Tag `RISK: no_selector_evidence`; do not guess |
