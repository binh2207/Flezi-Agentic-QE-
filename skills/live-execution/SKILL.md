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
| Execution report | `playwright-automation-framework/reports/execution-<feature>.md` |
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

Do not recapture if URL and visible structure are unchanged.

### MCP capture script

Use `browser_evaluate` / `playwright_evaluate` with this script on the live page:

```javascript
(() => {
  const stability = (el) => {
    if (el.dataset.testid || el.dataset.qa || el.dataset.cy) return 'data-attribute';
    if (el.getAttribute('aria-label') || el.getAttribute('role')) return 'aria';
    if (el.id) return 'id';
    return 'css';
  };

  const bestSelector = (el) => {
    if (el.dataset.testid) return `[data-testid="${el.dataset.testid}"]`;
    if (el.dataset.qa) return `[data-qa="${el.dataset.qa}"]`;
    if (el.dataset.cy) return `[data-cy="${el.dataset.cy}"]`;
    if (el.id) return `#${el.id}`;
    const name = el.getAttribute('name');
    if (name) return `${el.tagName.toLowerCase()}[name="${name}"]`;
    const aria = el.getAttribute('aria-label');
    if (aria) return `[aria-label="${aria}"]`;
    return null;
  };

  const labelFor = (el) => {
    if (el.id) {
      const lbl = document.querySelector(`label[for="${el.id}"]`);
      if (lbl) return lbl.textContent.trim();
    }
    const parent = el.closest('label');
    if (parent) return parent.textContent.trim();
    return el.getAttribute('aria-label') || el.getAttribute('placeholder') || null;
  };

  const seen = new Set();
  const elements = [];

  document
    .querySelectorAll(
      'input, button, select, textarea, a[href], [data-testid], [data-qa], [role="button"], [role="link"]',
    )
    .forEach((el) => {
      const sel = bestSelector(el);
      if (!sel || seen.has(sel)) return;
      seen.add(sel);
      const raw = (el.dataset.testid || el.getAttribute('name') || el.id || el.textContent || '')
        .trim()
        .slice(0, 40)
        .replace(/\s+/g, '_')
        .toLowerCase();
      elements.push({
        intent: raw || 'unknown',
        selector: sel,
        tag: el.tagName.toLowerCase(),
        type: el.getAttribute('type') || el.tagName.toLowerCase(),
        label: labelFor(el),
        text: el.textContent?.trim().slice(0, 80) || null,
        placeholder: el.getAttribute('placeholder') || null,
        visible: el.offsetParent !== null,
        stability: stability(el),
      });
    });

  return JSON.stringify(
    {
      page: document.title || '',
      url: window.location.href,
      route: window.location.pathname,
      build_id:
        document.querySelector('meta[name="app-build-id"]')?.getAttribute('content') || null,
      captured_at: new Date().toISOString(),
      element_count: elements.length,
      elements,
    },
    null,
    2,
  );
})()
```

Persist the JSON to `playwright-automation-framework/support/screen-maps/<feature>.screen.json`.

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
