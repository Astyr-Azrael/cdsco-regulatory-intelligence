from __future__ import annotations

import re
import unicodedata
from collections import defaultdict


EVALUATED_FIELDS = (
    "drug_name",
    "batch_number",
    "manufacturer",
    "manufacturing_date",
    "expiry_date",
    "failure_reason",
    "testing_laboratory",
    "sample_authority",
)


def normalized(value) -> str | None:
    if value is None:
        return None
    text = unicodedata.normalize("NFKC", str(value)).casefold()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split()) or None


def _score_pairs(expected: list, actual: list) -> dict:
    pairs = list(zip(expected, actual))
    applicable = [(left, right) for left, right in pairs if left is not None]
    labelled = len(applicable)
    exact = sum(left == right for left, right in applicable)
    normalized_exact = sum(normalized(left) == normalized(right) for left, right in applicable)
    true_positive = sum(
        left is not None and right is not None and normalized(left) == normalized(right)
        for left, right in pairs
    )
    false_positive = sum(
        right is not None and (left is None or normalized(left) != normalized(right))
        for left, right in pairs
    )
    # A wrong value both misses the expected value and introduces a wrong one.
    false_negative = sum(left is not None and normalized(left) != normalized(right) for left, right in pairs)
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else None
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else None
    denominator = 2 * true_positive + false_positive + false_negative
    f1 = 2 * true_positive / denominator if denominator else None
    return {
        "evaluated_rows": len(pairs),
        "labelled_values": labelled,
        "exact_match_accuracy": exact / labelled if labelled else None,
        "normalized_match_accuracy": normalized_exact / labelled if labelled else None,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "missing_field_rate": (
            sum(right is None for _, right in applicable) / labelled if labelled else None
        ),
    }


def evaluate_rows(ground_truth: list[dict], predictions: list[dict]) -> dict:
    key = lambda row: (row["source_document_id"], row["source_row"])
    predicted = {key(row): row for row in predictions}
    by_category: dict[str, list[dict]] = defaultdict(list)
    field_pairs: dict[str, tuple[list, list]] = {
        field: ([], []) for field in EVALUATED_FIELDS
    }
    missing_rows = []

    for expected_row in ground_truth:
        actual_row = predicted.get(key(expected_row))
        if actual_row is None:
            missing_rows.append({"source_document_id": key(expected_row)[0], "source_row": key(expected_row)[1]})
            actual_row = {}
        by_category[expected_row["alert_type"]].append((expected_row, actual_row))
        for field in EVALUATED_FIELDS:
            field_pairs[field][0].append(expected_row.get(field))
            field_pairs[field][1].append(actual_row.get(field))

    category_metrics = {}
    for category, pairs in by_category.items():
        category_metrics[category] = {
            field: _score_pairs(
                [expected.get(field) for expected, _ in pairs],
                [actual.get(field) for _, actual in pairs],
            )
            for field in EVALUATED_FIELDS
        }

    return {
        "labelled_rows": len(ground_truth),
        "predicted_rows": len(predictions),
        "matched_rows": len(ground_truth) - len(missing_rows),
        "missing_rows": missing_rows,
        "metrics_by_field": {
            field: _score_pairs(expected, actual)
            for field, (expected, actual) in field_pairs.items()
        },
        "metrics_by_category": category_metrics,
    }
