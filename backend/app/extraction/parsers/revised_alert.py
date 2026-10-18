from __future__ import annotations

from pathlib import Path

from backend.app.extraction.parsers.spurious import parse as parse_spurious_rows


def parse(path: str | Path, alert_type: str = "REVISED_ALERT") -> list[dict]:
    return parse_spurious_rows(path, alert_type=alert_type)
