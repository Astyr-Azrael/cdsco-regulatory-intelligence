from __future__ import annotations

import hashlib
import re
import unicodedata
from datetime import datetime
from pathlib import Path

import pdfplumber

from backend.app.extraction.parsers.models import PARSER_VERSION, TableRow


def clean_cell(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(unicodedata.normalize("NFKC", value).split()).strip()
    return cleaned or None


def parse_serial(value: str | None) -> int | None:
    cleaned = clean_cell(value)
    if not cleaned:
        return None
    match = re.fullmatch(r"(\d{1,4})\.?", cleaned)
    return int(match.group(1)) if match else None


def normalize_month_year(value: str | None) -> str | None:
    cleaned = clean_cell(value)
    if not cleaned or cleaned.casefold() in {"na", "n/a", "nm", "-"}:
        return None
    cleaned = cleaned.replace("–", "-").replace("/", "-")
    for pattern in ("%m-%Y", "%b-%Y", "%B-%Y", "%b-%y", "%B-%y"):
        try:
            return datetime.strptime(cleaned, pattern).strftime("%Y-%m")
        except ValueError:
            continue
    return None


def source_document_id(path: str | Path) -> str:
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return f"sha256:{digest}"


def iter_table_rows(path: str | Path) -> list[TableRow]:
    result: list[TableRow] = []
    with pdfplumber.open(path) as document:
        for page_number, page in enumerate(document.pages, start=1):
            for table in page.find_tables():
                extracted = table.extract()
                for index, cells in enumerate(extracted):
                    row_bbox = None
                    if index < len(table.rows):
                        boxes = [box for box in table.rows[index].cells if box is not None]
                        if boxes:
                            row_bbox = [
                                float(min(box[0] for box in boxes)),
                                float(min(box[1] for box in boxes)),
                                float(max(box[2] for box in boxes)),
                                float(max(box[3] for box in boxes)),
                            ]
                    result.append(TableRow(page_number=page_number, bbox=row_bbox, cells=cells))
    return result


def parse_status(values: dict, required: tuple[str, ...]) -> tuple[str, list[str]]:
    missing = [name for name in required if not values.get(name)]
    if not missing:
        return "PARSED", []
    if len(missing) <= max(1, len(required) // 3):
        return "PARTIAL", [f"Missing field: {name}" for name in missing]
    return "REQUIRES_REVIEW", [f"Missing field: {name}" for name in missing]


def make_record(
    *,
    path: str | Path,
    alert_type: str,
    parser_name: str,
    page_number: int,
    source_row: int,
    source_bbox: list[float] | None,
    raw_cells: list[str | None],
    fields: dict,
    required: tuple[str, ...],
    extra_warnings: list[str] | None = None,
) -> dict:
    status, warnings = parse_status(fields, required)
    warnings.extend(extra_warnings or [])
    if extra_warnings and status == "PARSED":
        status = "PARTIAL"
    cleaned_cells = [clean_cell(cell) for cell in raw_cells]
    return {
        "source_document_id": source_document_id(path),
        "source_filename": Path(path).name,
        "source_page": page_number,
        "source_row": source_row,
        "source_bbox": source_bbox,
        "alert_type": alert_type,
        "raw_cells": cleaned_cells,
        "raw_row_text": " | ".join(cell for cell in cleaned_cells if cell),
        **fields,
        "parse_status": status,
        "parser_name": parser_name,
        "parser_version": PARSER_VERSION,
        "warnings": warnings,
    }
