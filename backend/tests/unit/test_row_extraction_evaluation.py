from backend.app.evaluation.row_extraction import evaluate_rows


def test_evaluation_reports_exact_normalized_and_missing_metrics():
    truth = [
        {
            "source_document_id": "doc",
            "source_row": 1,
            "alert_type": "NSQ",
            "drug_name": "Drug  Name",
            "batch_number": "ABC-1",
            "manufacturer": None,
            "manufacturing_date": "Jan-2025",
            "expiry_date": "Dec-2026",
            "failure_reason": "Dissolution",
            "testing_laboratory": "CDL",
            "sample_authority": None,
        }
    ]
    predicted = [{**truth[0], "drug_name": "drug name", "batch_number": None}]

    report = evaluate_rows(truth, predicted)

    assert report["labelled_rows"] == 1
    assert report["matched_rows"] == 1
    assert report["metrics_by_field"]["drug_name"]["exact_match_accuracy"] == 0.0
    assert report["metrics_by_field"]["drug_name"]["normalized_match_accuracy"] == 1.0
    assert report["metrics_by_field"]["batch_number"]["missing_field_rate"] == 1.0
