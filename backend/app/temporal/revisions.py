def revision_key(title: str, month: str) -> tuple[str, str]:
    return (title.lower().replace("revised", "").strip(), month)
