---
name: project-extension
description: >-
  Project-specific overrides for custom components, auth strategy, and
  page object conventions. Read after pipeline-orchestrator phases when
  the project has a custom-components.md or auth-flow.md in inputs/project-config/.
  Does NOT modify core skills — extends only.
---

# Project Extension

Apply project-specific rules on top of the core harness pipeline. Core SKILL.md files are never modified.

## When to activate

Include this skill in your prompt when the project has any of:
- Custom UI components documented in `inputs/project-config/custom-components.md`
- Non-standard auth flow documented in `inputs/project-config/auth-flow.md`
- A project base page at `pages/<project>-base.page.ts`

Prompt example:
```
Run pipeline-orchestrator for feature "checkout".
Also apply: skills/project-extension/SKILL.md
Project config: inputs/project-config/
Flow: inputs/manual-flows/checkout.md
```

## Step 0 — Read project config (before any phase)

Before live-execution starts:

1. Check if `inputs/project-config/custom-components.md` exists — if yes, read it fully.
2. Check if `inputs/project-config/auth-flow.md` exists — if yes, read it fully.
3. Note the project base page name (e.g. `pages/acme-base.page.ts`) if present.

Keep this context for all subsequent phases — do not re-read these files per phase.

## Phase overrides

### live-execution overrides

- If auth is required: follow `auth-flow.md` strategy before executing any flow step.
- If a step interacts with a documented custom component: note the component name and helper path for Phase 2.
- Do not attempt to automate steps marked as `BLOCKER` in `auth-flow.md` — stop and report.

### automation-framework overrides

- Feature pages MUST extend the project base page (`pages/<project>-base.page.ts`), not `BasePage` directly.
- For any step involving a custom component from `custom-components.md`:
  - Import the helper from `support/components/<component>.ts`
  - Call the helper function instead of raw Playwright actions
  - Do NOT inline the component interaction logic in the page object
- If the component helper does not exist yet, create it under `support/components/` following `support/components/example-component.template.ts`.

### test-healer overrides

- If a selector fails and the element is a custom component: consult `custom-components.md` for the correct selector pattern before guessing.
- Component-internal selectors (e.g. `.ql-editor`, `.react-select__control`) are expected — do not flag as `RISK: heuristic_selector` if they match the documented pattern.

## File ownership

| File | Created by | Modified by |
|---|---|---|
| `inputs/project-config/custom-components.md` | QA / dev (copy from template) | QA when components change |
| `inputs/project-config/auth-flow.md` | QA / dev (copy from template) | QA when auth changes |
| `pages/<project>-base.page.ts` | Dev (copy from template) | Dev when adding component helpers |
| `support/components/<component>.ts` | AI or dev | AI during automation-framework phase |

## Core files — never touch

- `pages/base.page.ts`
- `support/helpers.ts`
- `support/capture-script.js`
- `fixtures/index.ts`
- `playwright.config.ts`
- Any file under `skills/` except this one
