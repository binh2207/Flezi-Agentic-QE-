---
name: test-case-design
description: Design manual QA test cases using professional test techniques (boundary value analysis, equivalence partitioning, decision tables, state transition, exploratory testing). Outputs structured test cases as Markdown (.md) files. Use when the user asks to create test cases, design test scenarios, generate test suites, write QA tests, or mentions test coverage for any feature or requirement.
---

# Test Case Design

Design comprehensive manual QA test cases and export them as Markdown files.

## Workflow

**Before designing any test cases, you MUST complete Step 0 first.**

### Step 0 — RAG context retrieval (recommended when KB is set up)

Query the RAG knowledge base with the feature/requirement to surface relevant context (existing test patterns, domain rules, prior decisions) before designing anything. See [docs/kb-guidelines.md](../../docs/kb-guidelines.md). Skip Step 0 only if the vector store is empty and requirements are provided another way.

```bash
python3 knowledge_base/vector/query.py "<feature or requirement>" --n 5
```

- Use the query results to inform test design: adopt existing naming conventions, avoid duplicating covered cases, and apply domain rules found in the retrieved chunks.
- If the ChromaDB store is empty (collection not found), ingest first:
  ```bash
  python3 knowledge_base/vector/ingest.py .
  ```
  Then re-run the query.
- Only proceed to Step 1 once you have reviewed the RAG output.

### Step 1 — Analyze

Analyze the feature/requirement provided by the user, incorporating any context retrieved from RAG.

### Step 2 — Identify

Identify applicable test design techniques.

### Step 3 — Design

Design test cases using the techniques below.

### Step 4 — Generate

Generate a Markdown file with all test cases.

## Test Design Techniques

### Boundary Value Analysis (BVA)

Identify input boundaries and test at, just below, and just above each boundary.

For a field accepting values 1–100:
- Invalid: 0, -1, 101, 999
- Boundary: 1, 2, 99, 100
- Nominal: 50

### Equivalence Partitioning (EP)

Divide input domain into classes where all values in a class behave identically. Test one representative from each class.

For an age field (valid: 18–65):
- Invalid class 1: < 18 → test with 10
- Valid class: 18–65 → test with 30
- Invalid class 2: > 65 → test with 70
- Invalid class 3: non-numeric → test with "abc"
- Invalid class 4: empty → test with ""

### Decision Table Testing

Map combinations of conditions to expected actions. Use when business rules have multiple interacting conditions.

| Condition          | R1  | R2  | R3  | R4  |
|--------------------|-----|-----|-----|-----|
| Premium member     | Y   | Y   | N   | N   |
| Order > $100       | Y   | N   | Y   | N   |
| **Free shipping**  | Y   | Y   | Y   | N   |
| **10% discount**   | Y   | Y   | N   | N   |

Create one test case per rule column.

### State Transition Testing

Model the system as states with transitions triggered by events.

1. Identify all states (e.g., Draft → Submitted → Approved → Rejected)
2. Identify transitions and triggers
3. Test every valid transition (0-switch coverage minimum)
4. Test invalid transitions (e.g., Draft → Approved directly)

### Exploratory Testing Scenarios

Design session-based charters for areas not fully covered by structured techniques.

Charter format:
> **Explore** [target area] **with** [resources/techniques] **to discover** [information/risks]

Example:
> Explore the checkout flow with slow network simulation to discover timeout handling issues.

## Test Case Structure

Each test case must include these fields:

| Field | Description |
|-------|-------------|
| TC_ID | Unique identifier (e.g., TC_LOGIN_001) |
| Module | Feature area or module name |
| Title | Short descriptive title |
| Preconditions | Setup required before execution |
| Steps | Numbered step-by-step actions |
| Test Data | Specific input values |
| Expected Result | What should happen |
| Priority | High / Medium / Low |
| Technique | BVA / EP / Decision Table / State Transition / Exploratory |
| Type | Positive / Negative / Edge Case |

## Generating Markdown Output

Use `scripts/test_case_writer.py` — `write_test_cases_markdown(feature, cases)` handles all formatting and writes to `inputs/test-cases/test_cases_<slug>.md`.

Each case dict keys: `tc_id`, `module`, `title`, `preconditions`, `steps` (list), `test_data`, `expected_result`, `priority`, `technique`, `case_type`.

```bash
python3 scripts/test_case_writer.py --feature "Login Form" --cases /path/to/cases.json
```

## Coverage Guidelines

Aim for this minimum coverage per feature:

- **Happy path**: At least 2-3 positive test cases
- **Negative testing**: At least 3-5 negative cases per input
- **Boundary values**: Test at every identified boundary
- **Error handling**: Verify all error messages and recovery paths
- **State coverage**: Cover all reachable states and key transitions

## Prioritization Rules

- **High**: Core functionality, security-critical, data integrity
- **Medium**: Important but non-blocking, alternate flows
- **Low**: UI polish, edge cases with low probability
