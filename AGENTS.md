# Agent instructions (all assistants)

This file is for **Cursor, Claude Code, GitHub Copilot, and other coding agents** working in this repository.

## QA users

Read [README.md — Guidelines for QA](README.md#guidelines-for-qa) and [docs/register-your-assistant.md](docs/register-your-assistant.md) to connect your editor.

## Project purpose

Application-agnostic **Playwright harness engineering**: live UI evidence → screen maps → POM automation → test run → optional self-healing.

## Skills (canonical)

All workflow skills live in [`skills/`](skills/):

| Priority | Skill | When |
|----------|-------|------|
| 1 | [pipeline-orchestrator](skills/pipeline-orchestrator/SKILL.md) | End-to-end feature automation |
| 2 | [live-execution](skills/live-execution/SKILL.md) | Browser evidence + screen maps |
| 3 | [automation-framework](skills/automation-framework/SKILL.md) | Generate POM from screen maps |
| 4 | [test-healer](skills/test-healer/SKILL.md) | Fix failing Playwright tests |

Optional: [test-case-design](skills/test-case-design/SKILL.md), [test-jira-reporter](skills/test-jira-reporter/SKILL.md), [knowledge-base](skills/knowledge-base/SKILL.md). KB guide: [docs/kb-guidelines.md](docs/kb-guidelines.md).

**Cursor / Claude Code:** `.cursor/skills` and `.claude/skills` symlink here.  
**Copilot:** follow [.github/copilot-instructions.md](.github/copilot-instructions.md).

## Non-negotiable rules

1. UI **selectors** come from `playwright-automation-framework/support/screen-maps/*.screen.json` only — never invent from training data or RAG.
2. Run **live-execution** before **automation-framework** if no screen map exists.
3. Generated code stays under `playwright-automation-framework/`.
4. Do not weaken product assertions to force tests green without explicit human approval.

## Key paths

| Path | Role |
|------|------|
| `inputs/manual-flows/` | QA flow input |
| `playwright-automation-framework/` | Playwright POM + tests |
| `skills/` | Agent skill definitions |
| `kb_server/` + `knowledge_base/` | Optional RAG (not for selectors) |
