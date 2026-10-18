import pytest

from backend.app.scraper.sources.cdsco_current_nsq import standardize_row, validate_payload


def sample_row():
    return {"str_product_name": "Example Tablets", "str_batch_no": "B-1", "dt_manufacturing_date": "Jan-2026", "dt_expiry_date": "Dec-2027", "str_manufactured_by": "Example Manufacturer", "str_nsq_result": "Dissolution", "str_reporting_source": "State Lab", "str_reported_by_lab_or_state": "Example DTL", "dt_reporting_month_year": "AUG-2026"}


def test_validates_and_standardizes_current_portal_row():
    payload = {"iTotalRecords": 1, "aaData": [sample_row()]}
    validate_payload(payload)
    row = standardize_row(payload["aaData"][0], 1)
    assert row["raw_drug_name"] == "Example Tablets"
    assert row["parsed_manufacturing_date"] == "2026-01"
    assert row["parse_status"] == "PARSED"
    assert row["source_page"] == 0


def test_rejects_count_mismatch():
    with pytest.raises(ValueError, match="count mismatch"):
        validate_payload({"iTotalRecords": 2, "aaData": [sample_row()]})
