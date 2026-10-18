from __future__ import annotations

from backend.app.entity_resolution.string_similarity import aggregate_similarity


def resolve_candidate(
    features: dict[str, float],
    threshold: float,
    *,
    review_threshold: float | None = None,
    compatible_context: bool = True,
) -> dict:
    score = aggregate_similarity(features)
    review_threshold = review_threshold if review_threshold is not None else max(0.0, threshold - 10.0)
    if compatible_context and score >= threshold:
        decision = "MATCH"
    elif score >= review_threshold:
        decision = "REVIEW"
    else:
        decision = "NO_MATCH"
    return {"score": score, "decision": decision, "threshold": threshold, "review_threshold": review_threshold}
