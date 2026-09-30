"""Conservative CDSCO alert-index spider scaffold.

Implement only after confirming current source URLs and crawl permissions. CAPTCHA or
anti-bot protections must never be bypassed.
"""

import scrapy


class AlertsSpider(scrapy.Spider):
    name = "cdsco_alerts"
    allowed_domains = ["cdsco.gov.in", "www.cdsco.gov.in"]
    start_urls = ["https://www.cdsco.gov.in/opencms/opencms/en/Notifications/Alerts/"]

    def parse(self, response):
        yield {"source_url": response.url, "status": "index-reached"}
