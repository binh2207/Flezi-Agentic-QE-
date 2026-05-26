# MCP setup — Playwright always on

Live harness execution needs a **browser MCP** server. This repo ships project config so Playwright MCP **auto-starts** with Cursor.

## One-time setup

```bash
npm run setup:mcp      # create/merge .mcp.json from .mcp.json.example
npm run verify:mcp     # npx resolves @playwright/mcp + config check
```

Then **reload MCP** in Cursor (restart Cursor or use MCP panel → refresh).

## What gets configured

[`.mcp.json.example`](../.mcp.json.example) defines:

| Server | Purpose | autoStart |
|--------|---------|-----------|
| `playwright` | `@playwright/mcp` — `browser_navigate`, `browser_snapshot`, … | yes |
| `jira` | Optional reporting (`mcp-atlassian`) | yes |

Local [`.mcp.json`](../.mcp.json) is gitignored (secrets). `setup:mcp` creates it or **adds** `playwright` if you already have Jira only.

## Tool names in skills

| MCP server | Example tools | Used by |
|------------|---------------|---------|
| `playwright` (project) | `browser_*` | [live-execution](../skills/live-execution/SKILL.md) |
| `plugin-playwright-playwright` | `browser_*` | Cursor plugin (fallback) |
| `user-playwright` | `playwright_*` | Legacy / codegen flows |

Skills prefer **`browser_*`** from project `playwright` or the Cursor plugin.

## Windows

If `npx` fails to start the server, use a `cmd` wrapper (see [playwright-mcp#658](https://github.com/microsoft/playwright-mcp/issues/658)):

```json
"playwright": {
  "command": "cmd",
  "args": ["/c", "npx", "-y", "@playwright/mcp@latest"],
  "alwaysAllow": true,
  "autoStart": true
}
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `playwright` red / not in MCP list | `npm run setup:mcp`, reload Cursor |
| Tool not found | Confirm server name is `playwright`; read tool schema before calling |
| Stale npx cache / connection closed | Clear `%LOCALAPPDATA%/npm-cache/_npx` (Windows) or `~/.npm/_npx`, rerun `verify:mcp` |
| Duplicate servers | Disable extra Playwright entries in **global** Cursor MCP if project `playwright` is enough |
| Copilot only | Run live-execution in Cursor; generate POM in Copilot (see [register-your-assistant.md](register-your-assistant.md)) |

## CI

`npm run verify:mcp` runs in GitHub Actions to ensure `@playwright/mcp` resolves (no live browser in CI).
