"""Run the bounded Phase 1 CDSCO index-to-intermediate-record pipeline."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.extraction.pdf_inspection import inspect_pdf
from backend.app.extraction.pdf_text import PdfExtractionError, extract_pdf_text
from backend.app.preprocessing.record_standardization import build_intermediate_record, write_jsonl
from backend.app.scraper.download import DocumentDownloadError, download_document
from backend.app.scraper.models import AlertMetadata
from backend.app.scraper.sources.cdsco_alert_index import DEFAULT_ALERTS_URL, fetch_alert_index

LOGGER = logging.getLogger("cdsco.phase1")
PREFERRED_TYPES = ("NSQ", "STATE_NSQ", "SPURIOUS", "REVISED_ALERT")


def select_representative_alerts(
    alerts: list[AlertMetadata], max_documents: int, *, categories: tuple[str, ...] = PREFERRED_TYPES,
    start_date: date | None = None, end_date: date | None = None,
) -> list[AlertMetadata]:
    eligible = []
    for alert in alerts:
        if not alert.document_url or alert.alert_type not in categories:
            continue
        published = date.fromisoformat(alert.publication_date) if alert.publication_date else None
        if start_date and (published is None or published < start_date):
            continue
        if end_date and (published is None or published > end_date):
            continue
        eligible.append(alert)
    selected: list[AlertMetadata] = []
    for alert_type in categories:
        match = next((item for item in eligible if item.alert_type == alert_type), None)
        if match is not None:
            selected.append(match)
        if len(selected) >= max_documents:
            return selected
    for alert in eligible:
        if alert not in selected:
            selected.append(alert)
        if len(selected) >= max_documents:
            break
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-url", default=DEFAULT_ALERTS_URL)
    parser.add_argument("--max-documents", type=int, default=5, choices=range(1, 51))
    parser.add_argument("--start-date", type=date.fromisoformat, help="Inclusive YYYY-MM-DD corpus boundary")
    parser.add_argument("--end-date", type=date.fromisoformat, help="Inclusive YYYY-MM-DD corpus boundary")
    parser.add_argument("--categories", nargs="+", choices=PREFERRED_TYPES, default=list(PREFERRED_TYPES))
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data" / "interim" / "cdsco_alert_records.jsonl",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    LOGGER.info("source access started: %s", args.source_url)
    snapshot, alerts = fetch_alert_index(
        PROJECT_ROOT / "data" / "raw" / "html", source_url=args.source_url
    )
    LOGGER.info("source access succeeded; alerts discovered: %d", len(alerts))
    categories = tuple(args.categories)
    selected = select_representative_alerts(alerts, args.max_documents, categories=categories, start_date=args.start_date, end_date=args.end_date)

    records: list[dict] = []
    audits: list[dict] = []
    failures: list[dict] = []
    for alert in selected:
        LOGGER.info("download started: %s", alert.alert_title)
        try:
            download = download_document(alert, PROJECT_ROOT / "data" / "raw" / "pdf")
            LOGGER.info(
                "%s: %s", "duplicate detected" if download.duplicate else "download completed", alert.alert_title
            )
            LOGGER.info("extraction started: %s", alert.alert_title)
            extraction = extract_pdf_text(download.local_raw_path)
            LOGGER.info("extraction completed: %s", alert.alert_title)
            records.append(
                build_intermediate_record(alert, download, extraction, project_root=PROJECT_ROOT)
            )
            audits.append(
                {
                    "alert_title": alert.alert_title,
                    "alert_type": alert.alert_type,
                    "publication_date": alert.publication_date,
                    "document_url": alert.document_url,
                    "resolved_document_url": download.resolved_document_url,
                    "content_hash_sha256": download.content_hash_sha256,
                    **inspect_pdf(download.local_raw_path, extraction),
                }
            )
            LOGGER.info("record prepared: %s", alert.alert_title)
        except (DocumentDownloadError, PdfExtractionError, OSError) as exc:
            LOGGER.error("document failed: %s: %s", alert.alert_title, exc)
            failures.append(
                {
                    "alert_title": alert.alert_title,
                    "document_url": alert.document_url,
                    "error": str(exc),
                }
            )

    write_jsonl(records, args.output)
    audit_output = args.output.with_name("cdsco_phase1_audit.json")
    audit_output.write_text(
        json.dumps(
            {
                "index_snapshot": {
                    "source_url": snapshot.source_url,
                    "retrieved_at": snapshot.retrieved_at,
                    "local_raw_path": str(Path(snapshot.local_raw_path).relative_to(PROJECT_ROOT)),
                    "content_hash_sha256": snapshot.content_hash_sha256,
                },
                "documents": audits,
                "failures": failures,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    corpus_manifest = args.output.with_name("bounded_corpus_manifest.json")
    corpus_manifest.write_text(json.dumps({"source_url": args.source_url, "start_date": args.start_date.isoformat() if args.start_date else None, "end_date": args.end_date.isoformat() if args.end_date else None, "categories": list(categories), "maximum_documents": args.max_documents, "selected_documents": [{"title": item.alert_title, "alert_type": item.alert_type, "publication_date": item.publication_date, "document_url": item.document_url} for item in selected]}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "alerts_discovered": len(alerts),
                "documents_selected": len(selected),
                "records_written": len(records),
                "failures": len(failures),
                "output": str(args.output),
                "audit_output": str(audit_output),
                "corpus_manifest": str(corpus_manifest),
            },
            indent=2,
        )
    )
    return 0 if records and not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
