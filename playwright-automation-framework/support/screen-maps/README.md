# Screen maps

JSON files here are the **selector source of truth** for generated automation.

- **Produced by:** [live-execution](../../../skills/live-execution/SKILL.md) (MCP browser capture)
- **Consumed by:** [automation-framework](../../../skills/automation-framework/SKILL.md) → pages, flows, specs
- **Schema:** [TEMPLATES.md](../../TEMPLATES.md#supportscreen-mapsfeaturescreenjson)

Naming: `<feature>.screen.json` (e.g. `checkout.screen.json` — matches your flow slug).

Do not hand-write selectors unless recapture is blocked — tag changes as `RISK:` in `reports/generation-manifest.json`.
