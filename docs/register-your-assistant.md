# Register the harness with your coding assistant

This guide helps **QA engineers** connect the Playwright harness to the assistant they already use: **Cursor**, **Claude Code**, or **GitHub Copilot**.

Skills live in one place: [`skills/`](../skills/). Cursor and Claude Code use symlinks; Copilot uses repository instructions.

---

## Before you register

1. Clone this repository and open it as your workspace root.
2. Run setup:
   ```bash
   npm run setup:playwright
   ```
3. Set `BASE_URL` in `playwright-automation-framework/.env`.
4. Enable browser MCP: `npm run setup:mcp && npm run verify:mcp`, then reload Cursor MCP ([MCP setup](mcp-setup.md)).
5. Read [README — Guidelines for QA](../README.md#guidelines-for-qa).

---

## Cursor

### What you get

- Project skills auto-discovered from `.cursor/skills/` (linked to `skills/`).
- Agent can run the full harness when you mention **pipeline-orchestrator** or paste a flow path.

### Register (project — recommended for QA)

1. Open the repo folder in **Cursor**.
2. Confirm skills exist: **Cursor Settings → Rules / Skills** (or ask the agent: “List available project skills”).
3. You should see skills such as `pipeline-orchestrator`, `live-execution`, `automation-framework`.
4. No copy step needed if you cloned this repo — symlinks are already configured.

### Register (personal — all your projects)

To use harness skills in **any** repo:

```bash
mkdir -p ~/.cursor/skills
for dir in skills/*/; do
  name=$(basename "$dir")
  ln -sf "$(pwd)/$dir" ~/.cursor/skills/harness-$name
done
```

Run from this repository root. Prefix `harness-` avoids name clashes.

### How to invoke (Cursor)

Example prompts:

```text
Run pipeline-orchestrator for feature "checkout".
Flow: inputs/manual-flows/checkout.md
```

```text
Use live-execution to capture a screen map for feature "login".
```

Tip: `@` mention a skill file if your Cursor version supports attaching skills to the chat.

---

## Claude Code

### What you get

- Skills under `.claude/skills/` (symlink to `skills/`).
- Root [CLAUDE.md](../CLAUDE.md) routes agents to QA guidelines and skills.

### Register

1. Install [Claude Code](https://docs.anthropic.com/en/docs/claude-code) if needed.
2. Open this repository in your terminal:
   ```bash
   cd /path/to/aiqe-playwright-harness
   claude
   ```
3. Claude Code reads `CLAUDE.md` and discovers skills in `.claude/skills/`.
4. Verify:
   ```text
   What harness skills are available in this project?
   ```

### Register (user-level skills)

Copy or link skills into Claude’s user skills directory (path may vary by version):

```bash
# Example: link into Claude Code user skills
mkdir -p ~/.claude/skills
for dir in skills/*/; do
  name=$(basename "$dir")
  ln -sf "$(pwd)/$dir" ~/.claude/skills/harness-$name
done
```

Check Anthropic docs for the current user skills path on your machine.

### How to invoke (Claude Code)

```text
Follow skills/pipeline-orchestrator/SKILL.md for feature checkout using inputs/manual-flows/checkout.md
```

---

## GitHub Copilot

### What you get

- Repository-wide instructions in [`.github/copilot-instructions.md`](../.github/copilot-instructions.md).
- Copilot does **not** use `SKILL.md` frontmatter the same way as Cursor; it follows `copilot-instructions.md` and files you open or reference.

### Register (VS Code)

1. Install **GitHub Copilot** and enable **Copilot Chat** / **Agent** (VS Code 1.96+ or compatible IDE).
2. Open this repository as the workspace folder (not a parent monorepo folder unless instructions are copied there).
3. Copilot automatically loads `.github/copilot-instructions.md` for this repo.
4. Optional: **VS Code → GitHub Copilot → Configure custom instructions** → ensure *Use instruction files* is enabled.

### Register (GitHub.com — Copilot coding agent)

If your org uses Copilot on GitHub Issues/PRs:

- Ensure this repo contains `.github/copilot-instructions.md` (already included).
- In prompts, reference: `skills/pipeline-orchestrator/SKILL.md` and your flow file path.

### How to invoke (Copilot)

```text
Follow .github/copilot-instructions.md and skills/pipeline-orchestrator/SKILL.md.
Run the harness for feature "checkout" using inputs/manual-flows/checkout.md.
BASE_URL is in playwright-automation-framework/.env.
```

For long workflows, ask Copilot to read one skill at a time:

1. `skills/live-execution/SKILL.md` — capture screen map  
2. `skills/automation-framework/SKILL.md` — generate POM  
3. `skills/test-healer/SKILL.md` — if tests fail  

### Copilot limitations

| Capability | Cursor / Claude Code | Copilot |
|------------|----------------------|---------|
| MCP browser (live-execution) | Yes, if MCP configured | Depends on IDE MCP; may need manual browser steps |
| Jira MCP | Yes | Limited; use manual Jira or test-jira-reporter outside Copilot |
| Terminal `npx playwright test` | Yes | Yes in VS Code |

If Copilot cannot drive MCP browser, QA runs **live-execution** in Cursor/Claude for capture, then continues automation generation in Copilot.

---

## Quick comparison

| Step | Cursor | Claude Code | Copilot |
|------|--------|-------------|---------|
| Open repo root | Yes | Yes | Yes |
| Skills auto-loaded | `.cursor/skills` | `.claude/skills` | `copilot-instructions.md` |
| Full pipeline prompt | `pipeline-orchestrator` | `skills/pipeline-orchestrator/SKILL.md` | Same + instructions file |
| Edit skills | `skills/` folder | `skills/` folder | `skills/` + instructions |

---

## Verify registration

Run this checklist after setup:

- [ ] `npm test` passes (2 skipped placeholders)
- [ ] Assistant lists or acknowledges `pipeline-orchestrator`
- [ ] `inputs/manual-flows/<your-feature>.md` exists
- [ ] `playwright-automation-framework/.env` has `BASE_URL`
- [ ] `npm run verify:mcp` passes; Cursor MCP shows **playwright** running
- [ ] Test prompt: “What is step 1 of pipeline-orchestrator?” → should mention **live-execution** and screen maps

---

## Updating skills

1. Edit only files under [`skills/`](../skills/).
2. Cursor and Claude Code pick up changes via symlink (restart chat if cached).
3. Copilot: changes apply on next session; re-read `copilot-instructions.md` if needed.

---

## Help

| Issue | Doc |
|-------|-----|
| QA workflow | [README.md](../README.md#guidelines-for-qa) |
| Deploy / fork | [DEPLOY.md](DEPLOY.md) |
| Skill index | [skills/README.md](../skills/README.md) |
