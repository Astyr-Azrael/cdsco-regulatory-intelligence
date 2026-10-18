from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AlertMetadata:
    alert_title: str
    alert_type: str | None
    publication_date: str | None
    document_url: str | None
    source_url: str
    retrieved_at: str
    pdf_size_text: str | None = None


@dataclass(frozen=True)
class IndexSnapshot:
    source_url: str
    retrieved_at: str
    local_raw_path: str
    content_hash_sha256: str
    http_status: int
    mime_type: str | None


@dataclass(frozen=True)
class DownloadResult:
    source_url: str
    document_url: str
    resolved_document_url: str
    retrieved_at: str
    original_filename: str
    local_raw_path: str
    content_hash_sha256: str
    http_status: int
    mime_type: str | None
    file_size_bytes: int
    duplicate: bool = False


@dataclass(frozen=True)
class PdfPageText:
    page_number: int
    text: str


@dataclass(frozen=True)
class PdfExtractionResult:
    page_count: int
    page_texts: list[PdfPageText]
    full_text: str
    extraction_success: bool
    extraction_method: str = "pymupdf"
    warnings: list[str] = field(default_factory=list)
