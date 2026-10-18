from __future__ import annotations

from pathlib import Path

from backend.app.extraction.parsers.central_nsq import parse as parse_eight_column_rows


def parse(path: str | Path, alert_type: str = "STATE_NSQ") -> list[dict]:
    return parse_eight_column_rows(path, alert_type=alert_type)
