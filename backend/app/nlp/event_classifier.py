def classify_event(title: str) -> str:
    lowered = title.lower()
    if "revised" in lowered or "corrigendum" in lowered:
        return "REVISED_ALERT"
    if "state" in lowered and "nsq" in lowered:
        return "STATE_NSQ"
    if "nsq" in lowered or "not of standard quality" in lowered:
        return "NSQ"
    return "OTHER"
