# Tests

| Directory | Purpose |
|-----------|---------|
| `smoke/` | Fast checks; `harness-placeholder` skips until real smoke specs exist |
| `e2e/` | Feature specs from **automation-framework**; `harness-placeholder` skips until generated |

Placeholders use `testInfo.skip()` so `npm test` exits 0 while the harness pipeline has not run yet.

Generated specs import from `fixtures/index.ts` and use screen maps under `support/screen-maps/`.
