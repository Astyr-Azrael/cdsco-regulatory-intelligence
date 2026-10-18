"""Conservative CDSCO alert-index spider that emits evidence-oriented metadata only."""

import scrapy

from backend.app.scraper.sources.cdsco_alert_index import parse_alert_index, utc_now


class AlertsSpider(scrapy.Spider):
    name = "cdsco_alerts"
    allowed_domains = ["cdsco.gov.in", "www.cdsco.gov.in"]
    start_urls = ["https://www.cdsco.gov.in/opencms/opencms/en/Notifications/Alerts/"]

    def parse(self, response):
        for alert in parse_alert_index(response.text, response.url, retrieved_at=utc_now()):
            yield {
                "alert_title": alert.alert_title,
                "alert_type": alert.alert_type,
                "publication_date": alert.publication_date,
                "document_url": alert.document_url,
                "source_url": alert.source_url,
                "retrieved_at": alert.retrieved_at,
                "pdf_size_text": alert.pdf_size_text,
            }
