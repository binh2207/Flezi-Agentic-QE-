# AIQE — Playwright Harness Engineering

Application-agnostic **AI harness for Playwright**. Consumer apps supply flows under `inputs/` and `BASE_URL`; generated automation lives under `playwright-automation-framework/`.

**QA users:** [README — Guidelines for QA](README.md#guidelines-for-qa) · [KB guidelines](docs/kb-guidelines.md) · [Register assistants](docs/register-your-assistant.md)

**All agents:** [AGENTS.md](AGENTS.md)

## Primary skill

### Harness Engineering (full pipeline)
- [skills/harness-engineering/SKILL.md](skills/harness-engineering/SKILL.md)
- Use when: building automation from a URL/flow, running the full harness, or "harness engineering" / "Playwright automation with AI"

## Harness phases

### Live execution (evidence + screen maps)
- [skills/live-execution/SKILL.md](skills/live-execution/SKILL.md)

### Automation framework (POM generation)
- [skills/automation-framework/SKILL.md](skills/automation-framework/SKILL.md)

### Playwright self-healing
- [skills/playwright-self-healing/SKILL.md](skills/playwright-self-healing/SKILL.md)

## Optional

### Test case design
- [skills/test-case-design/SKILL.md](skills/test-case-design/SKILL.md)

### JIRA test reporter
- [skills/test-jira-reporter/SKILL.md](skills/test-jira-reporter/SKILL.md)

### RAG / knowledge base (optional)
- [docs/kb-guidelines.md](docs/kb-guidelines.md)
- [skills/rag/SKILL.md](skills/rag/SKILL.md) — not for UI selectors

## Framework root

`playwright-automation-framework/` · Inputs: `inputs/manual-flows/`, `inputs/test-cases/`
