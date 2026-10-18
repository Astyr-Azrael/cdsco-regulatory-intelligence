from __future__ import annotations

from pathlib import Path

from backend.app.extraction.parsers.common import (
    clean_cell,
    iter_table_rows,
    make_record,
    normalize_month_year,
    parse_serial,
)


REQUIRED = (
    "drug_name",
    "batch_number",
    "manufacturing_date",
    "expiry_date",
    "manufacturer",
    "failure_reason",
    "testing_laboratory",
)


def parse(path: str | Path, alert_type: str = "NSQ") -> list[dict]:
    records: list[dict] = []
    for row in iter_table_rows(path):
        if len(row.cells) != 8:
            continue
        serial = parse_serial(row.cells[0])
        if serial is None:
            continue
        raw_mfg = clean_cell(row.cells[3])
        raw_expiry = clean_cell(row.cells[4])
        fields = {
            "drug_name": clean_cell(row.cells[1]),
            "batch_number": clean_cell(row.cells[2]),
            "manufacturing_date": raw_mfg,
            "expiry_date": raw_expiry,
            "parsed_manufacturing_date": normalize_month_year(raw_mfg),
            "parsed_expiry_date": normalize_month_year(raw_expiry),
            "manufacturer": clean_cell(row.cells[5]),
            "manufacturer_address": None,
            "failure_reason": clean_cell(row.cells[6]),
            "testing_laboratory": clean_cell(row.cells[7]),
            "sample_authority": None,
            "firm_reply": None,
            "remarks": None,
        }
        date_warnings = []
        if raw_mfg and not fields["parsed_manufacturing_date"]:
            date_warnings.append("Manufacturing date was retained but not normalized")
        if raw_expiry and not fields["parsed_expiry_date"]:
            date_warnings.append("Expiry date was retained but not normalized")
        records.append(
            make_record(
                path=path,
                alert_type=alert_type,
                parser_name="central_nsq" if alert_type == "NSQ" else "state_nsq",
                page_number=row.page_number,
                source_row=serial,
                source_bbox=row.bbox,
                raw_cells=row.cells,
                fields=fields,
                required=REQUIRED,
                extra_warnings=date_warnings,
            )
        )
    return records
