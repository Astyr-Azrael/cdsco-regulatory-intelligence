def link_events(entity_id: str, events: list[dict]) -> list[dict]:
    return sorted((event for event in events if event.get("entity_id") == entity_id), key=lambda item: item.get("event_date", ""))
