def candidate_keys(name: str, state: str | None = None) -> set[str]:
    tokens = {token for token in name.lower().split() if len(token) > 2}
    if state:
        tokens.add(state.lower())
    return tokens
