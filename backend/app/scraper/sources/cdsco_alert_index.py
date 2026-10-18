from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

import requests

from backend.app.preprocessing.text_cleaning import normalize_text
from backend.app.scraper.models import AlertMetadata, IndexSnapshot

DEFAULT_ALERTS_URL = "https://www.cdsco.gov.in/opencms/opencms/en/Notifications/Alerts/"
DEFAULT_USER_AGENT = "CDSCO-Regulatory-Intelligence-Academic-Research/0.1 (+non-commercial data audit)"


@dataclass
class _Cell:
    text: str
    href: str | None


class _AlertTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[_Cell]] = []
        self._row: list[_Cell] | None = None
        self._cell_parts: list[str] | None = None
        self._cell_href: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag == "tr":
            self._row = []
        elif tag in {"td", "th"} and self._row is not None:
            self._cell_parts = []
            self._cell_href = None
        elif tag == "a" and self._cell_parts is not None:
            self._cell_href = dict(attrs).get("href")
        elif tag == "br" and self._cell_parts is not None:
            self._cell_parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._cell_parts is not None:
            self._cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"td", "th"} and self._cell_parts is not None and self._row is not None:
            self._row.append(_Cell(normalize_text("".join(self._cell_parts)), self._cell_href))
            self._cell_parts = None
            self._cell_href = None
        elif tag == "tr" and self._row is not None:
            if self._row:
                self.rows.append(self._row)
            self._row = None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def classify_alert_type(title: str) -> str | None:
    value = normalize_text(title).casefold()
    if "availability of" in value and "new link" in value:
        return None
    if any(token in value for token in ("revised", "revise list", "corrigendum")) and any(
        context in value for context in ("drug alert", "nsq", "spurious")
    ):
        return "REVISED_ALERT"
    if "state" in value and ("nsq" in value or "not of standard quality" in value):
        return "STATE_NSQ"
    if "spurious" in value:
        return "SPURIOUS"
    if "nsq" in value or "not of standard quality" in value or "not of standard of quality" in value:
        return "NSQ"
    return None


def normalize_publication_date(value: str) -> str | None:
    cleaned = normalize_text(value)
    for pattern in ("%Y-%b-%d", "%Y-%B-%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(cleaned, pattern).date().isoformat()
        except ValueError:
            continue
    return None


def parse_alert_index(
    html: str,
    source_url: str = DEFAULT_ALERTS_URL,
    retrieved_at: str | None = None,
) -> list[AlertMetadata]:
    parser = _AlertTableParser()
    parser.feed(html)
    timestamp = retrieved_at or utc_now()
    records: list[AlertMetadata] = []

    for row in parser.rows:
        if len(row) < 5 or not row[0].text.isdigit():
            continue
        title = row[1].text
        if not title:
            continue
        link = row[3].href
        records.append(
            AlertMetadata(
                alert_title=title,
                alert_type=classify_alert_type(title),
                publication_date=normalize_publication_date(row[2].text),
                document_url=urljoin(source_url, link) if link else None,
                source_url=source_url,
                retrieved_at=timestamp,
                pdf_size_text=row[4].text or None,
            )
        )
    return records


def fetch_alert_index(
    raw_html_dir: str | Path,
    source_url: str = DEFAULT_ALERTS_URL,
    session: requests.Session | None = None,
    timeout: float = 30.0,
) -> tuple[IndexSnapshot, list[AlertMetadata]]:
    client = session or requests.Session()
    response = client.get(source_url, timeout=timeout, headers={"User-Agent": DEFAULT_USER_AGENT})
    response.raise_for_status()
    content = response.content
    digest = hashlib.sha256(content).hexdigest()
    retrieved_at = utc_now()

    target_dir = Path(raw_html_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"cdsco-alerts-{digest[:16]}.html"
    if not target_path.exists():
        target_path.write_bytes(content)

    encoding = response.encoding or "utf-8"
    html = content.decode(encoding, errors="replace")
    snapshot = IndexSnapshot(
        source_url=source_url,
        retrieved_at=retrieved_at,
        local_raw_path=str(target_path),
        content_hash_sha256=digest,
        http_status=response.status_code,
        mime_type=response.headers.get("Content-Type"),
    )
    return snapshot, parse_alert_index(html, source_url=source_url, retrieved_at=retrieved_at)
