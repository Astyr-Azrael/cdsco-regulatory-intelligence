"""Evaluate Phase 2 parsed rows against the frozen ground-truth subset."""

from __future__ import annotations

import json
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.evaluation.row_extraction import evaluate_rows


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--truth", type=Path, default=PROJECT_ROOT / "data" / "samples" / "ground_truth" / "regulatory_rows.jsonl")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "data" / "interim" / "row_extraction_evaluation.json")
    args = parser.parse_args()
    truth_path = args.truth
    parsed_path = PROJECT_ROOT / "data" / "interim" / "parsed_regulatory_records.jsonl"
    report = evaluate_rows(read_jsonl(truth_path), read_jsonl(parsed_path))
    output = args.output
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"labelled_rows": report["labelled_rows"], "matched_rows": report["matched_rows"], "output": str(output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
