"""Write a CSV execution report after live-execution runs."""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict


class StepResult(TypedDict):
    step: int
    action: str
    target: str
    expected_signal: str
    actual_result: str
    status: str        # PASS | FAIL | SKIP | ERROR
    url: str
    screenshot: str    # relative path from repo root, or ""
    timestamp: str     # ISO 8601


_CSV_FIELDS = [
    "step",
    "action",
    "target",
    "expected_signal",
    "actual_result",
    "status",
    "url",
    "screenshot",
    "timestamp",
]

_VALID_STATUSES = {"PASS", "FAIL", "SKIP", "ERROR"}
_OUTPUT_DIR = Path("playwright-automation-framework/reports")


class ExecutionReportWriter:
    """Converts live-execution step results into a CSV report.

    Usage (from an agent or script):

        from scripts.execution_report_writer import ExecutionReportWriter, StepResult

        writer = ExecutionReportWriter()
        path = writer.write("checkout", steps)
    """

    def __init__(self, output_dir: str | Path = _OUTPUT_DIR) -> None:
        self._output_dir = Path(output_dir)

    def write(self, feature: str, steps: list[StepResult]) -> Path:
        """Write *steps* to ``execution-<feature>.csv`` and return the path.

        Args:
            feature: The feature slug (e.g. ``"checkout"``).
            steps:   Ordered list of step results from live execution.

        Returns:
            Absolute path of the written CSV file.

        Raises:
            ValueError: If *feature* is empty or any step has an invalid status.
        """
        if not feature or not feature.strip():
            raise ValueError("feature must be a non-empty string")

        for i, step in enumerate(steps):
            status = str(step.get("status", "")).upper()
            if status not in _VALID_STATUSES:
                raise ValueError(
                    f"steps[{i}].status must be one of {sorted(_VALID_STATUSES)}, got {status!r}"
                )

        self._output_dir.mkdir(parents=True, exist_ok=True)
        path = self._output_dir / f"execution-{feature}.csv"

        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=_CSV_FIELDS, extrasaction="ignore")
            writer.writeheader()
            for step in steps:
                row = {field: step.get(field, "") for field in _CSV_FIELDS}
                row["status"] = str(row["status"]).upper()
                if not row["timestamp"]:
                    row["timestamp"] = datetime.now(timezone.utc).isoformat()
                writer.writerow(row)

        return path.resolve()

    def summary(self, steps: list[StepResult]) -> dict:
        """Return pass/fail/skip/error counts for *steps*."""
        counts: dict[str, int] = {"PASS": 0, "FAIL": 0, "SKIP": 0, "ERROR": 0, "total": len(steps)}
        for step in steps:
            key = str(step.get("status", "")).upper()
            if key in counts:
                counts[key] += 1
        return counts


def _load_steps(path: str) -> list[StepResult]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("steps JSON must be a list of step-result objects")
    return raw


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Write live-execution CSV report")
    parser.add_argument("--feature", required=True, help="Feature slug (e.g. checkout)")
    parser.add_argument("--steps", required=True, help="Path to JSON file with step results list")
    parser.add_argument(
        "--output-dir",
        default=str(_OUTPUT_DIR),
        help=f"Output directory (default: {_OUTPUT_DIR})",
    )
    args = parser.parse_args()

    steps = _load_steps(args.steps)
    writer = ExecutionReportWriter(output_dir=args.output_dir)
    out_path = writer.write(args.feature, steps)
    summary = writer.summary(steps)
    print(out_path)
    print(
        f"  {summary['total']} steps — "
        f"PASS:{summary['PASS']} FAIL:{summary['FAIL']} "
        f"SKIP:{summary['SKIP']} ERROR:{summary['ERROR']}"
    )
