def pairwise_metrics(true_pairs: set, predicted_pairs: set) -> dict[str, float]:
    true_positive = len(true_pairs & predicted_pairs)
    precision = true_positive / len(predicted_pairs) if predicted_pairs else 0.0
    recall = true_positive / len(true_pairs) if true_pairs else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}
