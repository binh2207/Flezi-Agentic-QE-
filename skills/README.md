# Agent skills (portable)

Canonical skill definitions for the Playwright harness. **Same content** is used by:

| Assistant | How it loads this folder |
|-----------|-------------------------|
| **Cursor** | `.cursor/skills` → symlink to `skills/` |
| **Claude Code** | `.claude/skills` → symlink to `skills/` |
| **GitHub Copilot** | [.github/copilot-instructions.md](../.github/copilot-instructions.md) + open `skills/*/SKILL.md` when needed |

**QA:** Register your assistant → [docs/register-your-assistant.md](../docs/register-your-assistant.md)

## Skills index

| Skill | Start here? | Purpose |
|-------|-------------|---------|
| [pipeline-orchestrator](pipeline-orchestrator/SKILL.md) | **Yes** | Full pipeline for one feature |
| [live-execution](live-execution/SKILL.md) | | MCP browser + screen maps |
| [automation-framework](automation-framework/SKILL.md) | | POM from screen maps |
| [test-healer](test-healer/SKILL.md) | | Fix failing tests |
| [test-jira-reporter](test-jira-reporter/SKILL.md) | | Jira report (optional) |
| [test-case-design](test-case-design/SKILL.md) | | Manual TC markdown (optional) |
| [knowledge-base](knowledge-base/SKILL.md) | | Requirements RAG only (optional) |

## Skill file format

Each `SKILL.md` uses YAML frontmatter (`name`, `description`) compatible with Cursor and Claude Code skill discovery.

Do not edit copies under `.cursor/skills` or `.claude/skills` directly — edit files **here** in `skills/`.
