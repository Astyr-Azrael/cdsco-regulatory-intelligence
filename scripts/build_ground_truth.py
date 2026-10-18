"""Freeze the visually reviewed 77-row Phase 2 ground-truth subset.

This script is intentionally separate from evaluation. Its output must be reviewed
against rendered PDFs before `verification_status` is retained.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.extract_regulatory_rows import extract_all


FIELDS = (
    "source_document_id",
    "source_filename",
    "source_page",
    "source_row",
    "source_bbox",
    "alert_type",
    "drug_name",
    "batch_number",
    "manufacturing_date",
    "expiry_date",
    "manufacturer",
    "manufacturer_address",
    "failure_reason",
    "testing_laboratory",
    "sample_authority",
    "firm_reply",
    "remarks",
    "raw_row_text",
)


def select_ground_truth(records: list[dict]) -> list[dict]:
    central = [row for row in records if row["alert_type"] == "NSQ"][:35]
    state = [row for row in records if row["alert_type"] == "STATE_NSQ"][:35]
    spurious = [row for row in records if row["alert_type"] == "SPURIOUS"]
    revised = [row for row in records if row["alert_type"] == "REVISED_ALERT"]
    selected = central + state + spurious + revised
    if len(selected) != 77:
        raise RuntimeError(f"Expected 77 labelled rows; selected {len(selected)}")
    return [
        {
            **{field: row.get(field) for field in FIELDS},
            "verification_status": "UNREVIEWED_PARSER_SEEDED",
            "verification_note": "Parser-seeded candidate only; independent PDF review is required before claiming verification.",
        }
        for row in selected
    ]


def main() -> int:
    output = PROJECT_ROOT / "data" / "samples" / "ground_truth" / "regulatory_rows.jsonl"
    if output.exists():
        raise SystemExit("Frozen labels already exist. Do not overwrite annotations with parser predictions.")
    rows = select_ground_truth(extract_all())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    print(json.dumps({"verified_rows": len(rows), "output": str(output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
