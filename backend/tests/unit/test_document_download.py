from __future__ import annotations

import hashlib
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pymupdf
import pytest

from backend.app.scraper.download import DocumentDownloadError, download_document
from backend.app.scraper.models import AlertMetadata


def _pdf_bytes() -> bytes:
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Official fixture document")
    content = document.tobytes()
    document.close()
    return content


@pytest.fixture
def document_server():
    pdf = _pdf_bytes()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/document.pdf":
                self.send_response(200)
                self.send_header("Content-Type", "application/pdf")
                self.send_header("Content-Disposition", 'attachment; filename="official.pdf"')
                self.end_headers()
                self.wfile.write(pdf)
            elif self.path == "/wrapper":
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b'<iframe src="/document.pdf"></iframe>')
            elif self.path == "/not-pdf":
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html>not a document</html>")
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", pdf
    finally:
        server.shutdown()
        thread.join()


def _alert(url: str) -> AlertMetadata:
    return AlertMetadata(
        alert_title="Official NSQ fixture",
        alert_type="NSQ",
        publication_date="2025-05-20",
        document_url=url,
        source_url="https://example.test/alerts",
        retrieved_at="2026-10-01T09:00:00Z",
    )


def test_download_hash_and_idempotency(tmp_path, document_server):
    base_url, content = document_server
    first = download_document(_alert(f"{base_url}/document.pdf"), tmp_path)
    second = download_document(_alert(f"{base_url}/document.pdf"), tmp_path)

    assert first.content_hash_sha256 == hashlib.sha256(content).hexdigest()
    assert first.original_filename == "official.pdf"
    assert first.duplicate is False
    assert second.duplicate is True
    assert first.local_raw_path == second.local_raw_path


def test_rejects_non_pdf_response(tmp_path, document_server):
    base_url, _ = document_server
    with pytest.raises(DocumentDownloadError, match="not a PDF"):
        download_document(_alert(f"{base_url}/not-pdf"), tmp_path)


def test_follows_same_host_official_download_wrapper(tmp_path, document_server):
    base_url, content = document_server
    result = download_document(_alert(f"{base_url}/wrapper"), tmp_path)
    assert result.resolved_document_url == f"{base_url}/document.pdf"
    assert result.content_hash_sha256 == hashlib.sha256(content).hexdigest()


def test_reports_http_failure(tmp_path, document_server):
    base_url, _ = document_server
    with pytest.raises(DocumentDownloadError, match="HTTP 404"):
        download_document(_alert(f"{base_url}/missing"), tmp_path)
