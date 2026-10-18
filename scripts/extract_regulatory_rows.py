"""Extract row-level records from the preserved Phase 1 CDSCO PDFs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.extraction.parsers.router import parse_regulatory_rows
from scripts.benchmark_extraction import alert_type_for


def extract_all() -> list[dict]:
    records: list[dict] = []
    for path in sorted((PROJECT_ROOT / "data" / "raw" / "pdf").glob("*.pdf")):
        records.extend(parse_regulatory_rows(path, alert_type_for(path)))
    return records


def main() -> int:
    records = extract_all()
    output = PROJECT_ROOT / "data" / "interim" / "parsed_regulatory_records.jsonl"
    output.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )
    status_counts = {
        status: sum(record["parse_status"] == status for record in records)
        for status in ("PARSED", "PARTIAL", "REQUIRES_REVIEW", "FAILED")
    }
    print(json.dumps({"records_written": len(records), "statuses": status_counts, "output": str(output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
