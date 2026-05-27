---
name: test-jira-reporter
description: Analyze Playwright test results and update a JIRA ticket with a structured test report comment. Reads the test execution output and test cases markdown, writes a formatted QA report as a JIRA comment, and optionally transitions the ticket status based on pass/fail outcome.
---

# JIRA Test Reporter

Analyze automated test results from the Playwright run and post a structured QA report to a JIRA ticket.

## MCP tools (use actual server + tool names)

Check enabled Jira MCP servers before calling (Cursor: **CallMcpTool**; Claude Code: MCP tools per IDE; Copilot: may require manual Jira update if MCP unavailable). Use server id and tool names from the MCP tool descriptors (e.g. `user-jira`).

### Preferred: `user-jira`

| Step | Server | Tool | Arguments |
|------|--------|------|-----------|
| Read ticket | `user-jira` | `read_jira_issue` | `{ "issueKey": "PROJ-123", "expand": "fields,transitions" }` |
| Post comment | `user-jira` | `add_jira_comment` | `{ "issueKey": "PROJ-123", "body": "<comment>" }` |
| Transition | `user-jira` | `transition_jira_issue` | `{ "issueKey": "PROJ-123", "transitionName": "In Review" }` |

### Alternative: `plugin-atlassian-atlassian`

| Step | Tool | Arguments |
|------|------|-----------|
| Read ticket | `getJiraIssue` | per tool schema (`issueIdOrKey`) |
| Post comment | `addCommentToJiraIssue` | per tool schema |
| Transition | `transitionJiraIssue` | per tool schema |

If neither server is available, report the blocker and skip JIRA steps.

## Inputs required

| Input | Source |
|-------|--------|
| JIRA ticket key | User (e.g. `PROJ-123`) |
| Flow / test cases | `inputs/manual-flows/<feature>.md` or `inputs/test-cases/test_cases_<feature>.md` |
| Playwright output | `cd playwright-automation-framework && npm test` |
| Spec file | `playwright-automation-framework/tests/e2e/<feature>.spec.ts` |
| Manifest | `playwright-automation-framework/reports/generation-manifest.json` |

## Workflow

### 1. Read the JIRA ticket

Call `read_jira_issue` (or `getJiraIssue`) to get summary, status, assignee, and available transitions.

### 2. Analyze test results

| Metric | How to derive |
|--------|----------------|
| Total TCs designed | Count `## TC_` headers in markdown (or flow steps) |
| Total automated | Count `test(` in spec file |
| Passed / failed / skipped | Parse Playwright list reporter output |
| Verdict | PASS if 0 failures |

### 3. Compose the JIRA comment

Use `scripts/jira_report_writer.py` — `JiraReportWriter.build_comment()` produces the full wiki-markup body. Pass the result as `body` to `add_jira_comment`.

### 4. Post the comment

Call `add_jira_comment` with `issueKey` and `body`.

### 5. Transition (optional)

| Verdict | Try `transitionName` |
|---------|----------------------|
| PASS | `In Review`, `QA Passed`, `Done` |
| FAIL | `In Progress`, `QA Failed` |

Skip silently if the transition is not in the ticket’s available transitions list.

## Output summary

Call `JiraReportWriter().summary_line(ticket_key, verdict, comment_body)` and print the result.

## Error handling

| Situation | Action |
|-----------|--------|
| No ticket key | Ask user |
| Ticket not found | Report error; skip comment |
| No Playwright output | Note in comment |
| Transition fails | Skip; comment still posted |
