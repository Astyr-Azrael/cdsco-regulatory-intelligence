from rapidfuzz import fuzz


def similarity_features(left: str, right: str) -> dict[str, float]:
    """Return interpretable RapidFuzz scores on a 0-100 scale."""
    return {
        "ratio": float(fuzz.ratio(left, right)),
        "weighted_ratio": float(fuzz.WRatio(left, right)),
        "token_sort_ratio": float(fuzz.token_sort_ratio(left, right)),
        "token_set_ratio": float(fuzz.token_set_ratio(left, right)),
    }


def aggregate_similarity(features: dict[str, float]) -> float:
    if not features:
        return 0.0
    return round(
        0.45 * features.get("weighted_ratio", 0.0)
        + 0.35 * features.get("token_set_ratio", 0.0)
        + 0.20 * features.get("ratio", 0.0),
        2,
    )
