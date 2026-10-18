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
    "sample_authority",
)


def _mapping(cells: list[str | None]) -> dict | None:
    if len(cells) == 10:
        return {
            "product_indexes": (1,),
            "batch": 2,
            "mfg": 3,
            "expiry": 4,
            "manufacturer": 5,
            "reason": 6,
            "authority": 7,
            "reply": 8,
            "remarks": 9,
        }
    if len(cells) == 12:
        return {
            "product_indexes": (1, 2, 3),
            "batch": 4,
            "mfg": 5,
            "expiry": 6,
            "manufacturer": 7,
            "reason": 8,
            "authority": 9,
            "reply": 10,
            "remarks": 11,
        }
    return None


def _product_fragment(cells: list[str | None], indexes: tuple[int, ...]) -> str | None:
    values = [clean_cell(cells[index]) for index in indexes if index < len(cells)]
    return clean_cell(" ".join(value for value in values if value))


def parse(path: str | Path, alert_type: str = "SPURIOUS") -> list[dict]:
    table_rows = iter_table_rows(path)
    assembled: list[dict] = []
    current: dict | None = None

    for table_row in table_rows:
        mapping = _mapping(table_row.cells)
        if mapping is None:
            continue
        serial = parse_serial(table_row.cells[0])
        if serial is not None:
            if current is not None:
                assembled.append(current)
            current = {
                "serial": serial,
                "page_number": table_row.page_number,
                "bbox": table_row.bbox,
                "cells": list(table_row.cells),
                "mapping": mapping,
                "product_parts": [],
            }
            fragment = _product_fragment(table_row.cells, mapping["product_indexes"])
            if fragment:
                current["product_parts"].append(fragment)
        elif current is not None and table_row.page_number == current["page_number"]:
            fragment = _product_fragment(table_row.cells, current["mapping"]["product_indexes"])
            if fragment:
                current["product_parts"].append(fragment)
            current["cells"].extend(table_row.cells)
            if table_row.bbox and current["bbox"]:
                current["bbox"][3] = max(current["bbox"][3], table_row.bbox[3])

    if current is not None:
        assembled.append(current)

    records: list[dict] = []
    for item in assembled:
        cells = item["cells"]
        mapping = item["mapping"]
        raw_mfg = clean_cell(cells[mapping["mfg"]])
        raw_expiry = clean_cell(cells[mapping["expiry"]])
        fields = {
            "drug_name": clean_cell(" ".join(item["product_parts"])),
            "batch_number": clean_cell(cells[mapping["batch"]]),
            "manufacturing_date": raw_mfg,
            "expiry_date": raw_expiry,
            "parsed_manufacturing_date": normalize_month_year(raw_mfg),
            "parsed_expiry_date": normalize_month_year(raw_expiry),
            "manufacturer": clean_cell(cells[mapping["manufacturer"]]),
            "manufacturer_address": None,
            "failure_reason": clean_cell(cells[mapping["reason"]]),
            "testing_laboratory": None,
            "sample_authority": clean_cell(cells[mapping["authority"]]),
            "firm_reply": clean_cell(cells[mapping["reply"]]),
            "remarks": clean_cell(cells[mapping["remarks"]]),
        }
        records.append(
            make_record(
                path=path,
                alert_type=alert_type,
                parser_name="spurious" if alert_type == "SPURIOUS" else "revised_alert",
                page_number=item["page_number"],
                source_row=item["serial"],
                source_bbox=item["bbox"],
                raw_cells=item["cells"],
                fields=fields,
                required=REQUIRED,
            )
        )
    return records
