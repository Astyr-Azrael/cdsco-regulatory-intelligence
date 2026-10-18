from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TableRow:
    page_number: int
    bbox: list[float] | None
    cells: list[str | None]


PARSER_VERSION = "phase2-0.1.0"
