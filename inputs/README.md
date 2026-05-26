# Harness inputs (your application)

This directory holds **your** flows and test cases. The framework under `playwright-automation-framework/` is application-agnostic.

**QA:** [Guidelines](../README.md#guidelines-for-qa) · [KB (optional)](../docs/kb-guidelines.md) · [Register assistants](../docs/register-your-assistant.md)

| Folder | Purpose |
|--------|---------|
| `manual-flows/` | Steps for live-execution / harness |
| `test-cases/` | Formal TC markdown (test-case-design) |
| `requirements/` | SRS and requirements from discovery (e.g. live-execution) |

| Path | Purpose |
|------|---------|
| `manual-flows/` | Step-by-step journeys for live-execution + automation generation |
| `test-cases/` | Optional structured TC markdown from test-case-design |

## Add a feature

1. Copy `manual-flows/example-flow.template.md` → `manual-flows/<your-feature>.md`
2. Set `BASE_URL` in `playwright-automation-framework/.env`
3. Run **harness-engineering** with feature slug `<your-feature>`

Consumer-specific flows and generated automation are **gitignored** by default (see root `.gitignore`). Only `example-flow.template.md` ships with the core framework.
