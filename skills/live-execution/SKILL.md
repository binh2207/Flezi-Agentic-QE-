---
name: live-execution
description: >-
  Executes flows against a live web app using MCP Playwright, captures screen maps
  and evidence, and writes reports. Required before automation-framework generation.
  Screen maps go to playwright-automation-framework/support/screen-maps/.
---

# Live execution (MCP Playwright)

Evidence-first execution for harness engineering. **Screen maps are the contract** for all downstream automation.

## Output locations

| Artifact | Path |
|----------|------|
| Screen map | `playwright-automation-framework/support/screen-maps/<feature>.screen.json` |
| Execution report (markdown) | `playwright-automation-framework/reports/execution-<feature>.md` |
| **Execution report (CSV)** | `playwright-automation-framework/reports/execution-<feature>.csv` |
| Screenshots | `playwright-automation-framework/reports/screenshots/` |

## Workflow

1. Load flow from `inputs/manual-flows/<feature>.md` or `inputs/test-cases/test_cases_<feature>.md`
2. Normalize steps (explicit action + target + expected signal)
3. Navigate to `BASE_URL` or the flow URL (MCP: `browser_navigate` / `playwright_navigate`)
4. **Capture screen map** on each new route/modal **before** clicks
5. Execute steps; record pass/fail and actual results
6. On failure: screenshot + console snippet + last URL

## Screen map capture

### When to capture

- Right after landing on a new route
- After a modal, drawer, or panel opens
- After a state change reveals new controls (post-login, post-search)

### Differential capture (skip if unchanged)

Before running the capture script, check if a screen map already exists for this route:

1. If `support/screen-maps/<feature>.screen.json` exists, read its `dom_fingerprint` and `route`.
2. Run the capture script and compare the returned `dom_fingerprint` with the stored value.
3. If fingerprints match **and** the route matches: reuse the existing map — do **not** overwrite.
4. Only write a new map when fingerprints differ or no map exists.

This avoids re-embedding the same DOM data multiple times in a session.

### MCP capture script

Use `browser_evaluate` / `playwright_evaluate` with the script at:

```
playwright-automation-framework/support/capture-script.js
```

Read the file content, then pass it verbatim as the expression argument to the MCP tool.

Persist the returned JSON to `playwright-automation-framework/support/screen-maps/<feature>.screen.json`.

**Before handoff:** review and rename `intent` values to stable snake_case (e.g. `cookie_accept`, `search_button`). Add `dom_fingerprint` and `freshness` per [TEMPLATES.md](../../playwright-automation-framework/TEMPLATES.md).

## Freshness (reuse existing maps)

| Condition | Status | Action |
|-----------|--------|--------|
| `route` or `build_id` mismatch | STALE_HARD | Recapture |
| `dom_fingerprint` drift > 0.20 | STALE_HARD | Recapture |
| Age > 7 days | STALE_SOFT | Recapture in same run if possible |

## MCP servers

1. **Project `playwright`** — run `npm run setup:mcp` once; uses `@playwright/mcp` (`browser_*` tools, `autoStart` in `.mcp.json`).
2. **Fallback** — `plugin-playwright-playwright` or `cursor-ide-browser` if project MCP is unavailable.

Read each tool schema before calling. Details: [docs/mcp-setup.md](../../docs/mcp-setup.md).

## Gates

- Do not hand off to **automation-framework** without a screen map for the primary route
- Tag `RISK: stale_map_soft` if continuing on STALE_SOFT

---

## Post-condition: CSV execution report

After all steps are executed, write a CSV report using `scripts/execution_report_writer.py`.

### CSV format

File: `playwright-automation-framework/reports/execution-<feature>.csv`

| Column | Type | Description |
|--------|------|-------------|
| `step` | int | Step number (1-based, matches flow table) |
| `action` | string | Action taken (e.g. `Click`, `Fill`, `Navigate`) |
| `target` | string | Element intent or route (e.g. `submit_button`, `/checkout`) |
| `expected_signal` | string | Expected outcome copied from the flow definition |
| `actual_result` | string | What actually happened (observed URL, text, or error) |
| `status` | enum | `PASS` \| `FAIL` \| `SKIP` \| `ERROR` |
| `url` | string | Page URL at the time the step was evaluated |
| `screenshot` | string | Repo-relative path to screenshot, or empty string |
| `timestamp` | ISO 8601 | UTC timestamp of step completion |

### Step status rules

| Status | When to use |
|--------|-------------|
| `PASS` | Expected signal observed exactly |
| `FAIL` | Step executed but expected signal not observed |
| `SKIP` | Step not executed (conditional branch or blocked by prior FAIL) |
| `ERROR` | Unexpected exception, timeout, or MCP tool failure |

### How to generate

Use `scripts/execution_report_writer.py` — `ExecutionReportWriter` class:

```bash
python scripts/execution_report_writer.py --feature <slug> --steps <steps.json>
```

### Agent checklist (post-execution)

After the final step:

1. Assemble `steps` list — one entry per flow step, in order
2. Set `screenshot` to the repo-relative path for every `FAIL` or `ERROR` step
3. Call `ExecutionReportWriter().write(feature, steps)`
4. Log the returned path and the summary counts
5. If any step is `FAIL` or `ERROR`, tag `RISK: execution_failures` in the generation manifest
