"""Benchmark four extraction methods on every preserved bounded-corpus PDF."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.extraction.benchmark import benchmark_document


def alert_type_for(path: Path) -> str:
    name = path.name.casefold()
    if "state-nsq" in name:
        return "STATE_NSQ"
    if "revise-list" in name:
        return "REVISED_ALERT"
    if "spurious" in name:
        return "SPURIOUS"
    return "NSQ"


def main() -> int:
    documents = sorted((PROJECT_ROOT / "data" / "raw" / "pdf").glob("*.pdf"))
    if len(documents) < 5:
        raise SystemExit(f"Expected at least five preserved PDFs; found {len(documents)}")
    results = [benchmark_document(path, alert_type_for(path)) for path in documents]
    output = PROJECT_ROOT / "data" / "interim" / "extraction_benchmark.json"
    output.write_text(json.dumps({"documents": results}, indent=2), encoding="utf-8")
    print(json.dumps({"documents_benchmarked": len(results), "output": str(output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
