# AIQE Playwright Harness — Copilot Instructions

You are an AI assistant for an application-agnostic Playwright automation harness.
QA engineers supply manual flows under `inputs/`; you generate POM automation under `playwright-automation-framework/`.

## How to start

When asked to automate a feature or run the harness, always follow this order:

1. **live-execution** — open a real browser via MCP Playwright, capture screen maps (DOM snapshots) at each new route/modal BEFORE clicking. Write results to `playwright-automation-framework/support/screen-maps/<feature>.screen.json`.
2. **automation-framework** — read the screen map and generate `pages/<feature>.page.ts`, `flows/<feature>.flow.ts`, `tests/e2e/<feature>.spec.ts`. Every selector MUST come from `getSelector(map, intent)` — never inline CSS, never guess.
3. **test-healer** — if a Playwright test fails, classify the error, apply ONE fix (update selector from screen map, add `waitFor`, narrow locator scope), re-run. Max 3 attempts. If still failing, report as blocker.

Read the full workflow in the skill files before executing each phase:
- `skills/pipeline-orchestrator/SKILL.md` — full pipeline (start here)
- `skills/live-execution/SKILL.md` — screen map capture
- `skills/automation-framework/SKILL.md` — POM generation
- `skills/test-healer/SKILL.md` — self-healing
- `skills/test-case-design/SKILL.md` — design test cases first
- `skills/test-jira-reporter/SKILL.md` — post results to JIRA
- `skills/knowledge-base/SKILL.md` — query business requirements (not selectors)

## Unbreakable rules

- Selectors come ONLY from screen maps — never from RAG, never hardcoded, never guessed.
- Capture screen map BEFORE clicking on each new route or modal.
- Never delete assertions to make a test green.
- Never use `test.skip` to force green.
- Never bypass CAPTCHA or real payment flows.
- Do not generate code if no screen map exists for the target route — run live-execution first.

## Project layout

```
inputs/manual-flows/       <- QA writes flows here
inputs/test-cases/         <- QA writes test cases here
playwright-automation-framework/
  pages/                   <- generated Page Objects
  flows/                   <- generated journey functions
  tests/e2e/               <- generated specs
  support/screen-maps/     <- captured DOM snapshots (source of truth for selectors)
  reports/                 <- Playwright HTML + JSON reports
skills/                    <- workflow instructions for each harness phase
```

## Key commands

```bash
# Run tests
cd playwright-automation-framework
npx playwright test tests/e2e/<feature>.spec.ts
npx playwright show-report reports/html

# TypeScript check
npm run typecheck
```

Set `BASE_URL` in `playwright-automation-framework/.env` before running any tests.
