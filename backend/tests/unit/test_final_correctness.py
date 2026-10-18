from backend.app.evaluation.row_extraction import evaluate_rows
from backend.app.preprocessing.drug_normalization import normalize_drug_name,drug_parts,compatible_products


def test_wrong_nonempty_extraction_counts_as_fp_and_fn():
    truth=[{"source_document_id":"x","source_row":1,"alert_type":"NSQ","manufacturer":"A"}]
    prediction=[{**truth[0],"manufacturer":"B"}]
    metrics=evaluate_rows(truth,prediction)["metrics_by_field"]["manufacturer"]
    assert metrics["false_positive"]==1 and metrics["false_negative"]==1
    assert metrics["recall"]==0 and metrics["precision"]==0
    assert metrics["f1"]==0


def test_decimal_strength_and_concentration_are_distinct():
    assert normalize_drug_name("Drug 2.5mg") != normalize_drug_name("Drug 25mg")
    assert normalize_drug_name("Drug 1mg/5ml") != normalize_drug_name("Drug 1mg 5ml")
    assert not compatible_products(drug_parts("Rosuvas F 10 Tablets"),drug_parts("Rosuvas F 20 Tablets"))
    assert not compatible_products(drug_parts("Drug Injection IP"),drug_parts("Drug Injection BP"))
