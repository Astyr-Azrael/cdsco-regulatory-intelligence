from __future__ import annotations

import hashlib
import os
import re
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

import requests

from backend.app.scraper.models import AlertMetadata, DownloadResult
from backend.app.scraper.sources.cdsco_alert_index import DEFAULT_USER_AGENT, utc_now


class DocumentDownloadError(RuntimeError):
    """Raised when an official document cannot be safely preserved."""


class _IframeSourceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.source: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "iframe" and self.source is None:
            self.source = dict(attrs).get("src")


def _slug(value: str, limit: int = 80) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return (result[:limit].rstrip("-") or "cdsco-document")


def _original_filename(response: requests.Response, alert: AlertMetadata) -> str:
    disposition = response.headers.get("Content-Disposition", "")
    match = re.search(r"filename\*?=(?:UTF-8''|\")?([^\";]+)", disposition, flags=re.IGNORECASE)
    if match:
        return Path(unquote(match.group(1).strip())).name
    path_name = Path(unquote(urlparse(response.url).path)).name
    return path_name if path_name.lower().endswith(".pdf") else f"{_slug(alert.alert_title)}.pdf"


def _resolve_download_response(
    client: requests.Session,
    response: requests.Response,
    document_url: str,
    timeout: float,
) -> requests.Response:
    """Follow the official same-host iframe used by CDSCO's download wrapper."""
    content_type = response.headers.get("Content-Type", "").lower()
    if "text/html" not in content_type:
        return response

    parser = _IframeSourceParser()
    parser.feed(response.text)
    if not parser.source:
        return response
    resolved_url = urljoin(response.url, parser.source)
    if urlparse(resolved_url).hostname != urlparse(document_url).hostname:
        raise DocumentDownloadError(f"Download wrapper points to a different host: {resolved_url}")
    response.close()
    return client.get(
        resolved_url,
        timeout=timeout,
        headers={"User-Agent": DEFAULT_USER_AGENT},
        stream=True,
    )


def download_document(
    alert: AlertMetadata,
    raw_pdf_dir: str | Path,
    session: requests.Session | None = None,
    timeout: float = 60.0,
) -> DownloadResult:
    if not alert.document_url:
        raise DocumentDownloadError(f"Alert has no document URL: {alert.alert_title}")

    client = session or requests.Session()
    response: requests.Response | None = None
    try:
        response = client.get(
            alert.document_url,
            timeout=timeout,
            headers={"User-Agent": DEFAULT_USER_AGENT},
            stream=True,
        )
        response = _resolve_download_response(client, response, alert.document_url, timeout)
    except requests.RequestException as exc:
        if response is not None:
            response.close()
        raise DocumentDownloadError(f"Request failed for {alert.document_url}: {exc}") from exc
    except DocumentDownloadError:
        if response is not None:
            response.close()
        raise
    if response.status_code != 200:
        response.close()
        raise DocumentDownloadError(f"HTTP {response.status_code} for {alert.document_url}")

    target_dir = Path(raw_pdf_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    digest = hashlib.sha256()
    prefix = b""
    size = 0
    try:
        with tempfile.NamedTemporaryFile(delete=False, dir=target_dir, suffix=".download") as temporary:
            temporary_path = Path(temporary.name)
            for chunk in response.iter_content(chunk_size=64 * 1024):
                if not chunk:
                    continue
                if len(prefix) < 5:
                    prefix += chunk[: 5 - len(prefix)]
                digest.update(chunk)
                temporary.write(chunk)
                size += len(chunk)
        mime_type = response.headers.get("Content-Type")
        if not prefix.startswith(b"%PDF"):
            raise DocumentDownloadError(
                f"Response is not a PDF for {alert.document_url} (Content-Type: {mime_type!r})"
            )

        content_hash = digest.hexdigest()
        date_part = alert.publication_date or "undated"
        filename = f"{date_part}_{_slug(alert.alert_title)}_{content_hash[:12]}.pdf"
        target_path = target_dir / filename
        duplicate = target_path.exists()
        if duplicate:
            temporary_path.unlink(missing_ok=True)
        else:
            os.replace(temporary_path, target_path)
        temporary_path = None

        return DownloadResult(
            source_url=alert.source_url,
            document_url=alert.document_url,
            resolved_document_url=response.url,
            retrieved_at=utc_now(),
            original_filename=_original_filename(response, alert),
            local_raw_path=str(target_path),
            content_hash_sha256=content_hash,
            http_status=response.status_code,
            mime_type=mime_type,
            file_size_bytes=size,
            duplicate=duplicate,
        )
    except requests.RequestException as exc:
        raise DocumentDownloadError(f"Request failed for {alert.document_url}: {exc}") from exc
    finally:
        response.close()
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
