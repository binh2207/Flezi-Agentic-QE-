"""Write structured test cases to Markdown (optional harness input)."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import TypedDict


class TestCase(TypedDict):
    tc_id: str
    module: str
    title: str
    preconditions: str
    steps: list[str]
    test_data: str
    expected_result: str
    priority: str
    technique: str
    case_type: str


def _slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower().strip())
    return slug.strip("_")


def _steps_block(steps: list[str]) -> str:
    lines = [f"{index}. {step}" for index, step in enumerate(steps, 1)]
    return "\n".join(lines)


def _render_case(case: TestCase) -> str:
    return f"""## {case["tc_id"]} — {case["title"]}

| Field | Value |
|-------|-------|
| **Module** | {case["module"]} |
| **Priority** | {case["priority"]} |
| **Technique** | {case["technique"]} |
| **Type** | {case["case_type"]} |

**Preconditions:** {case["preconditions"]}

**Steps:**
{_steps_block(case["steps"])}

**Test Data:** {case["test_data"]}

**Expected Result:** {case["expected_result"]}

---
"""


def write_test_cases_markdown(
    feature_name: str,
    cases: list[TestCase],
    output_dir: str | Path = "inputs/test-cases",
) -> Path:
    """Render test cases and write `test_cases_<feature_slug>.md`. Returns the file path."""
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)

    high = sum(1 for row in cases if row["priority"].lower() == "high")
    medium = sum(1 for row in cases if row["priority"].lower() == "medium")
    low = sum(1 for row in cases if row["priority"].lower() == "low")

    header = f"""# Test Cases: {feature_name}

## Summary
- **Total:** {len(cases)} test cases
- **High:** {high} | **Medium:** {medium} | **Low:** {low}

---

"""
    body = "".join(_render_case(row) for row in cases)
    path = root / f"test_cases_{_slug(feature_name)}.md"
    path.write_text(header + body, encoding="utf-8")
    return path


def _load_cases(raw: str) -> list[TestCase]:
    parsed = json.loads(raw)
    if not isinstance(parsed, list):
        msg = "cases JSON must be a list of test case objects"
        raise ValueError(msg)
    return parsed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Write test cases to Markdown")
    parser.add_argument("--feature", required=True, help="Feature name for the output file")
    parser.add_argument("--cases", required=True, help="Path to JSON file with test case list")
    parser.add_argument(
        "--output-dir",
        default="inputs/test-cases",
        help="Directory for the generated markdown file",
    )
    args = parser.parse_args()

    cases = _load_cases(Path(args.cases).read_text(encoding="utf-8"))
    path = write_test_cases_markdown(args.feature, cases, output_dir=args.output_dir)
    print(path)
