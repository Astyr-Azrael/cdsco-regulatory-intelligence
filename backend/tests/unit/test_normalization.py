from backend.app.preprocessing.batch_normalization import normalize_batch
from backend.app.preprocessing.manufacturer_normalization import normalize_manufacturer


def test_batch_normalization():
    assert normalize_batch(" mo24h27 ") == "MO24H27"


def test_manufacturer_suffixes():
    assert normalize_manufacturer("M/s. Example Pharma Pvt. Ltd.") == "Example Pharma Private Limited"
