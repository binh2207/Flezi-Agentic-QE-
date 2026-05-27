# AIQE — Playwright Harness Engineering

Application-agnostic **AI harness for Playwright**. Consumer apps supply flows under `inputs/` and `BASE_URL`; generated automation lives under `playwright-automation-framework/`.

**QA users:** [README — Guidelines for QA](README.md#guidelines-for-qa) · [KB guidelines](docs/kb-guidelines.md) · [Register assistants](docs/register-your-assistant.md)

**All agents:** [AGENTS.md](AGENTS.md)

## Primary skill

### Pipeline Orchestrator (full pipeline)
- [skills/pipeline-orchestrator/SKILL.md](skills/pipeline-orchestrator/SKILL.md)
- Use when: building automation from a URL/flow, running the full harness, or "harness engineering" / "Playwright automation with AI"

## Harness phases

### Live execution (evidence + screen maps)
- [skills/live-execution/SKILL.md](skills/live-execution/SKILL.md)

### Automation framework (POM generation)
- [skills/automation-framework/SKILL.md](skills/automation-framework/SKILL.md)

### Test healer (self-healing)
- [skills/test-healer/SKILL.md](skills/test-healer/SKILL.md)

## Optional

### Test case design
- [skills/test-case-design/SKILL.md](skills/test-case-design/SKILL.md)

### JIRA test reporter
- [skills/test-jira-reporter/SKILL.md](skills/test-jira-reporter/SKILL.md)

### Knowledge base / RAG (optional)
- [docs/kb-guidelines.md](docs/kb-guidelines.md)
- [skills/knowledge-base/SKILL.md](skills/knowledge-base/SKILL.md) — not for UI selectors

## Framework root

`playwright-automation-framework/` · Inputs: `inputs/manual-flows/`, `inputs/test-cases/`
