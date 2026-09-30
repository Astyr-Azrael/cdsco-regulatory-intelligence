def resolve_candidate(features: dict[str, float], threshold: float) -> dict:
    score = sum(features.values()) / max(len(features), 1)
    return {"score": score, "decision": "match" if score >= threshold else "review"}
