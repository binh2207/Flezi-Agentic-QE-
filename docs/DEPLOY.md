# Deploying the Playwright harness

Use this repo as a **template** or copy pieces into an existing project. The harness is application-agnostic; your app lives in `inputs/` and generated files under `playwright-automation-framework/`.

## What to ship vs what stays local

| In git (template) | Local / gitignored (per app) |
|-------------------|------------------------------|
| `skills/` (+ `.cursor/skills`, `.claude/skills` symlinks) | `inputs/manual-flows/<feature>.md` |
| `playwright-automation-framework/` scaffold | `support/screen-maps/*.json` |
| `inputs/manual-flows/example-flow.template.md` | Generated pages, flows, e2e specs |
| `TEMPLATES.md`, `base.page.ts`, placeholders | `reports/generation-manifest.json` |
| `scripts/`, `docs/` | `.env` with real `BASE_URL` |

See root `.gitignore` for the full list.

## Option A — Use as a standalone repo

1. Clone or fork this repository.
2. Run setup:
   ```bash
   npm run setup:playwright
   ```
3. Add your flow:
   ```bash
   cp inputs/manual-flows/example-flow.template.md inputs/manual-flows/my-feature.md
   ```
4. Set `BASE_URL` in `playwright-automation-framework/.env`.
5. In Cursor, run the **harness-engineering** skill with feature slug `my-feature`.
6. Commit only what your team policy allows (often generated specs; rarely screen maps if they contain sensitive selectors).

## Option B — Copy into an existing monorepo

Copy these paths into your repo (adjust names if needed):

```text
skills/                    # canonical (or symlink .cursor/skills → skills)
AGENTS.md
.github/copilot-instructions.md
docs/register-your-assistant.md
playwright-automation-framework/    # or merge into your existing e2e package
inputs/manual-flows/
scripts/setup-playwright.sh
```

Merge `package.json` scripts:

```json
{
  "scripts": {
    "test": "npm run test --prefix playwright-automation-framework",
    "setup:playwright": "bash scripts/setup-playwright.sh"
  }
}
```

Point agents at `skills/`, `AGENTS.md`, and [register-your-assistant.md](register-your-assistant.md).

## Option C — Optional knowledge base (RAG)

Not required for Playwright selectors. Only for requirements / test-case context.

```bash
npm run setup:kb
export ANTHROPIC_API_KEY=...
npm run kb:serve
```

Components: `knowledge_base/` (ingest, vector store, agent) + `kb_server/` (FastAPI).

## CI

GitHub Actions workflow: [.github/workflows/harness-ci.yml](../.github/workflows/harness-ci.yml)

Runs on push/PR:

- `npm ci` in `playwright-automation-framework/`
- `npx tsc --noEmit`
- `npm test` (skipped placeholders; exit 0)

Add your generated e2e specs to the repo (or generate in CI with secrets for `BASE_URL` and MCP — advanced).

## MCP (browser + JIRA)

1. Run `npm run setup:mcp` (Playwright MCP + optional Jira). See [mcp-setup.md](mcp-setup.md).
2. Set env vars for Jira (`ATLASSIAN_*`) if using **test-jira-reporter**.
3. Enable **cursor-ide-browser** or **plugin-playwright-playwright** for **live-execution**.

## First feature checklist

- [ ] `inputs/manual-flows/<feature>.md` filled in
- [ ] `BASE_URL` in `.env`
- [ ] **live-execution** → `support/screen-maps/<feature>.screen.json`
- [ ] **automation-framework** → pages, flows, `tests/e2e/<feature>.spec.ts`
- [ ] `npx playwright test tests/e2e/<feature>.spec.ts`
- [ ] Remove `harness-placeholder` specs when real tests exist
- [ ] **playwright-self-healing** if failures are timing/selectors only

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `BASE_URL is required` | `cp playwright-automation-framework/.env.example .env` and set URL |
| `No tests found` | Do not use `test.skip(true)` at definition level; use `testInfo.skip()` inside the test |
| `No screen map entry for intent` | Recapture screen map or align `selectors.ts` intents with JSON |
| Agent invents selectors | Enforce **live-execution** gate before **automation-framework** |
