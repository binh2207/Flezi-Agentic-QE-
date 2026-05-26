# GitHub Copilot — Playwright harness instructions

You are helping QA and engineers use the **AIQE Playwright Harness** in this repository.

## Read first

- QA workflow: [README.md](../README.md#guidelines-for-qa)
- Register Copilot: [docs/register-your-assistant.md](../docs/register-your-assistant.md#github-copilot)
- Full agent routing: [AGENTS.md](../AGENTS.md)

## Default workflow

When the user asks to automate a web flow or run the harness:

1. Read [skills/harness-engineering/SKILL.md](../skills/harness-engineering/SKILL.md) and follow it.
2. Use the user’s flow file under `inputs/manual-flows/<feature>.md`.
3. Use `BASE_URL` from `playwright-automation-framework/.env`.
4. Live browser capture needs MCP Playwright in Cursor (`npm run setup:mcp` — see `docs/mcp-setup.md`).
5. Execute sub-skills in order:
   - [skills/live-execution/SKILL.md](../skills/live-execution/SKILL.md) — screen maps **before** generation
   - [skills/automation-framework/SKILL.md](../skills/automation-framework/SKILL.md) — POM only from screen maps
   - Run `cd playwright-automation-framework && npx playwright test tests/e2e/<feature>.spec.ts`
   - [skills/playwright-self-healing/SKILL.md](../skills/playwright-self-healing/SKILL.md) on failure (max 3 attempts)

## Rules

- Never invent CSS selectors; use `support/screen-maps/<feature>.screen.json`.
- Never skip live capture when no screen map exists.
- Do not remove assertions to make tests pass.
- Optional Jira: [skills/test-jira-reporter/SKILL.md](../skills/test-jira-reporter/SKILL.md).

## Skill index

See [skills/README.md](../skills/README.md).

## Commands

```bash
npm run setup:playwright
npm test
npm run test:regression
```

Templates: `playwright-automation-framework/TEMPLATES.md`
