from backend.app.preprocessing.batch_normalization import normalize_batch
from backend.app.preprocessing.manufacturer_normalization import normalize_manufacturer
from backend.app.preprocessing.drug_normalization import drug_parts, normalize_drug_name


def test_batch_normalization():
    assert normalize_batch(" mo24h27 ") == "MO24H27"


def test_manufacturer_suffixes():
    assert normalize_manufacturer("M/s. Example Pharma Pvt. Ltd.") == "example pharma private limited"


def test_drug_normalization_preserves_strength_and_form():
    left = drug_parts("Telmisartan Tablets I.P. 40 mg")
    right = drug_parts("telmisartan tablets IP 40mg")
    assert left["normalized_name"] == right["normalized_name"]
    assert left["strengths"] == ("40mg",)
    assert left["dosage_forms"] == ("tablets",)


def test_drug_strengths_remain_distinct():
    assert normalize_drug_name("Amoxycillin Capsules IP 250 mg") != normalize_drug_name("Amoxycillin Capsules IP 500 mg")
