from pathlib import Path

from backend.app.scraper.sources.cdsco_alert_index import classify_alert_type, parse_alert_index
from scripts.process_documents import select_representative_alerts


FIXTURE = Path(__file__).parents[1] / "fixtures" / "cdsco_alert_index.html"


def test_parses_title_date_type_and_absolute_document_url():
    records = parse_alert_index(
        FIXTURE.read_text(encoding="utf-8"),
        source_url="https://example.test/alerts/",
        retrieved_at="2026-10-01T09:00:00Z",
    )

    assert len(records) == 2
    assert records[0].alert_type == "NSQ"
    assert records[0].publication_date == "2025-05-20"
    assert records[0].document_url == "https://example.test/files/april.pdf"
    assert records[0].retrieved_at == "2026-10-01T09:00:00Z"
    assert records[1].alert_type == "STATE_NSQ"
    assert records[1].document_url is None


def test_unexpected_html_returns_no_records():
    assert parse_alert_index("<html><p>No alert table</p></html>") == []


def test_non_record_notices_are_not_misclassified():
    assert classify_alert_type("Availability of NSQ Alert on New Link") is None
    assert classify_alert_type("Circular regarding recent revised GST rate Structure") is None
    assert classify_alert_type("Revise list drug alert May-2025") == "REVISED_ALERT"


def test_bounded_corpus_selection_filters_dates_and_categories():
    from datetime import date
    records = parse_alert_index(FIXTURE.read_text(encoding="utf-8"), source_url="https://example.test/alerts/", retrieved_at="2026-10-01T09:00:00Z")
    selected = select_representative_alerts(records, 10, categories=("NSQ",), start_date=date(2025, 5, 1), end_date=date(2025, 5, 31))
    assert len(selected) == 1
    assert selected[0].alert_type == "NSQ"
