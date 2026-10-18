from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import requests

from backend.app.extraction.parsers.common import normalize_month_year


PAGE_URL = "https://cdscoonline.gov.in/CDSCO/viewPublicNSQDrug"
DATA_URL = "https://cdscoonline.gov.in/CDSCO/publicNsqDrugTable"
REQUIRED_KEYS = {
    "str_product_name", "str_batch_no", "dt_manufacturing_date", "dt_expiry_date",
    "str_manufactured_by", "str_nsq_result", "str_reporting_source",
    "str_reported_by_lab_or_state", "dt_reporting_month_year",
}


def fetch_current_nsq(*, user_agent: str, timeout: int = 30) -> tuple[bytes, dict]:
    response = requests.get(DATA_URL, headers={"User-Agent": user_agent, "Accept": "application/json,text/plain,*/*"}, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    validate_payload(payload)
    return response.content, payload


def validate_payload(payload: dict) -> None:
    if not isinstance(payload, dict) or not isinstance(payload.get("aaData"), list):
        raise ValueError("Current NSQ response does not contain an aaData list")
    declared = payload.get("iTotalRecords")
    if declared is not None and int(declared) != len(payload["aaData"]):
        raise ValueError(f"Current NSQ response count mismatch: declared {declared}, received {len(payload['aaData'])}")
    for index, item in enumerate(payload["aaData"], start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Current NSQ row {index} is not an object")
        missing = REQUIRED_KEYS.difference(item)
        if missing:
            raise ValueError(f"Current NSQ row {index} is missing keys: {sorted(missing)}")


def save_raw_response(content: bytes, directory: Path) -> tuple[Path, str]:
    digest = hashlib.sha256(content).hexdigest()
    directory.mkdir(parents=True, exist_ok=True)
    month = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = directory / f"{month}_current_nsq_{digest[:12]}.json"
    if not path.exists():
        path.write_bytes(content)
    return path, digest


def standardize_row(item: dict, position: int) -> dict:
    raw_mfg = item.get("dt_manufacturing_date") or None
    raw_expiry = item.get("dt_expiry_date") or None
    warnings = []
    if raw_mfg and not normalize_month_year(raw_mfg): warnings.append("Manufacturing date was retained but not normalized")
    if raw_expiry and not normalize_month_year(raw_expiry): warnings.append("Expiry date was retained but not normalized")
    required_values = [item.get("str_product_name"), item.get("str_batch_no"), item.get("str_manufactured_by"), item.get("str_nsq_result")]
    status = "PARSED" if all(required_values) and not warnings else "PARTIAL"
    return {
        "source_page": 0, "source_row": position, "source_bbox": None, "alert_type": "NSQ",
        "raw_drug_name": item.get("str_product_name") or None, "raw_batch_number": item.get("str_batch_no") or None,
        "raw_manufacturer": item.get("str_manufactured_by") or None, "raw_manufacturer_address": None,
        "raw_manufacturing_date": raw_mfg, "raw_expiry_date": raw_expiry,
        "raw_failure_reason": item.get("str_nsq_result") or None,
        "raw_laboratory": item.get("str_reported_by_lab_or_state") or None, "raw_authority": None,
        "raw_remarks": None, "raw_firm_reply": None, "raw_cells": item,
        "raw_row_text": json.dumps(item, ensure_ascii=False, sort_keys=True),
        "parsed_manufacturing_date": normalize_month_year(raw_mfg), "parsed_expiry_date": normalize_month_year(raw_expiry),
        "parse_status": status, "parser_name": "current_portal_nsq", "parser_version": "phase2-0.1.0", "warnings": warnings,
    }
