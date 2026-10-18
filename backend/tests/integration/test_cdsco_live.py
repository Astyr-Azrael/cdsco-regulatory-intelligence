import os

import pytest

from backend.app.scraper.sources.cdsco_alert_index import fetch_alert_index


@pytest.mark.live
@pytest.mark.skipif(
    os.getenv("RUN_LIVE_CDSCO_TESTS") != "1",
    reason="Set RUN_LIVE_CDSCO_TESTS=1 to access the official CDSCO site",
)
def test_official_alert_index_exposes_document_records(tmp_path):
    snapshot, alerts = fetch_alert_index(tmp_path)
    assert snapshot.http_status == 200
    assert alerts
    assert any(alert.document_url for alert in alerts)
    assert any(alert.alert_type == "NSQ" for alert in alerts)
