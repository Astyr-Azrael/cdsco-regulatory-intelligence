"""Fetch one official CDSCO alert index and preserve its raw HTML plus metadata."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.scraper.sources.cdsco_alert_index import DEFAULT_ALERTS_URL, fetch_alert_index


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-url", default=DEFAULT_ALERTS_URL)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data" / "interim" / "cdsco_alert_metadata.json",
    )
    args = parser.parse_args()

    snapshot, alerts = fetch_alert_index(
        PROJECT_ROOT / "data" / "raw" / "html", source_url=args.source_url
    )
    selected_alerts = alerts[: max(0, args.limit)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {"index_snapshot": asdict(snapshot), "alerts": [asdict(item) for item in selected_alerts]},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "source_url": snapshot.source_url,
                "raw_html": snapshot.local_raw_path,
                "alerts_discovered": len(alerts),
                "records_written": len(selected_alerts),
                "output": str(args.output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
