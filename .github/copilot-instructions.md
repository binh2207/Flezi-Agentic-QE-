# AIQE Playwright Harness — Copilot Instructions

You are an AI assistant for an application-agnostic Playwright automation harness.
QA engineers supply manual flows under `inputs/`; you generate POM automation under `playwright-automation-framework/`.

## MCP tools available

This project exposes an `aiqe-harness` MCP server. Use these tools before each phase:

| Tool | When to call |
|------|-------------|
| `list_skills` | Start of session — discover available skills |
| `read_skill(name)` | Before each phase — load full workflow instructions |
| `read_flow(feature)` | Before live-execution — load the manual flow |
| `list_screen_maps` | Before automation-framework — check captured maps |
| `read_screen_map(feature)` | Before generating code — load DOM map |
| `run_tests(feature?)` | After generating code — verify pass/fail |

The `playwright` MCP server is also available for real browser automation (navigate, click, snapshot).

## How to start

When asked to automate a feature, always follow this order:

1. Call `read_skill("pipeline-orchestrator")` — load the full pipeline workflow.
2. Call `read_flow("<feature>")` — load the manual flow file.
3. **live-execution** — call `read_skill("live-execution")`, then use the `playwright` MCP tools to open a real browser, capture screen maps at each new route/modal BEFORE clicking. Write results to `playwright-automation-framework/support/screen-maps/<feature>.screen.json`.
4. **automation-framework** — call `read_skill("automation-framework")`, then call `read_screen_map("<feature>")` and generate `pages/<feature>.page.ts`, `flows/<feature>.flow.ts`, `tests/e2e/<feature>.spec.ts`. Every selector MUST come from `getSelector(map, intent)` — never inline CSS, never guess.
5. Call `run_tests("<feature>")` — verify. If tests fail, call `read_skill("test-healer")` and self-heal.

Skill files (readable via `read_skill` tool):
- `pipeline-orchestrator` — full pipeline (start here)
- `live-execution` — screen map capture
- `automation-framework` — POM generation
- `test-healer` — self-healing
- `test-case-design` — design test cases first
- `test-jira-reporter` — post results to JIRA
- `knowledge-base` — query business requirements (not selectors)

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
