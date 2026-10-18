from __future__ import annotations

from pathlib import Path

from backend.app.extraction.parsers import central_nsq, revised_alert, spurious, state_nsq


PARSERS = {
    "NSQ": central_nsq.parse,
    "STATE_NSQ": state_nsq.parse,
    "SPURIOUS": spurious.parse,
    "REVISED_ALERT": revised_alert.parse,
}


def parse_regulatory_rows(path: str | Path, alert_type: str) -> list[dict]:
    try:
        parser = PARSERS[alert_type]
    except KeyError as exc:
        raise ValueError(f"Unsupported alert type: {alert_type}") from exc
    return parser(path, alert_type=alert_type)
