from backend.app.entity_resolution.candidate_generation import generate_candidate_pairs
from backend.app.entity_resolution.resolver import resolve_candidate
from backend.app.entity_resolution.string_similarity import similarity_features


def test_candidate_generation_blocks_by_name_tokens():
    items = [
        {"normalized_name": "example pharma private limited", "display_name": "Example Pharma", "normalized_address": "baddi solan"},
        {"normalized_name": "example pharma limited", "display_name": "Example Pharma Ltd", "normalized_address": "baddi solan"},
        {"normalized_name": "unrelated remedies", "display_name": "Unrelated Remedies", "normalized_address": "goa"},
    ]
    pairs = generate_candidate_pairs(items)
    assert len(pairs) == 1
    assert pairs[0][0]["display_name"] == "Example Pharma"


def test_rapidfuzz_baseline_returns_interpretable_decision():
    features = similarity_features("example pharma private limited", "example pharma limited")
    result = resolve_candidate(features, 80.0, review_threshold=70.0, compatible_context=True)
    assert result["decision"] == "MATCH"
    assert 80 <= result["score"] <= 100


def test_context_can_prevent_a_high_name_score_match():
    features = similarity_features("example pharma private limited", "example pharma private limited")
    result = resolve_candidate(features, 96.0, review_threshold=86.0, compatible_context=False)
    assert result["decision"] == "REVIEW"
