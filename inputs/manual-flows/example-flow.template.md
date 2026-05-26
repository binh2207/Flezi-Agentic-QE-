# <Feature name> — manual flow

**App URL:** ${BASE_URL}/<path>

| Step | Action | Expected signal |
|------|--------|-----------------|
| 1 | Navigate to entry route | Page loads; key landmark visible |
| 2 | Accept cookie/consent if shown | Banner dismissed |
| 3 | Complete primary user action | Success message or next route |
| 4 | Assert boundary state | URL or heading matches acceptance criteria |

Replace placeholders, then use as input to **live-execution** and **automation-framework**.
