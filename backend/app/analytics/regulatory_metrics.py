def event_counts(events: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for event in events:
        kind = event.get("event_type", "OTHER")
        counts[kind] = counts.get(kind, 0) + 1
    return counts
