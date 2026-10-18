from backend.app.extraction.parsers import central_nsq, spurious
from backend.app.extraction.parsers.models import TableRow


def test_central_nsq_maps_eight_columns(monkeypatch, tmp_path):
    path = tmp_path / "central.pdf"
    path.write_bytes(b"source evidence")
    monkeypatch.setattr(
        central_nsq,
        "iter_table_rows",
        lambda _: [
            TableRow(
                1,
                [10.0, 20.0, 500.0, 80.0],
                ["1.", "Drug IP", "B123", "01/2025", "12/2027", "M/s Example, Address", "Dissolution", "CDL"],
            )
        ],
    )

    records = central_nsq.parse(path)

    assert records[0]["source_row"] == 1
    assert records[0]["batch_number"] == "B123"
    assert records[0]["parsed_manufacturing_date"] == "2025-01"
    assert records[0]["source_bbox"] == [10.0, 20.0, 500.0, 80.0]
    assert records[0]["parse_status"] == "PARSED"


def test_spurious_repairs_split_product_continuation_rows(monkeypatch, tmp_path):
    path = tmp_path / "spurious.pdf"
    path.write_bytes(b"source evidence")
    rows = [
        TableRow(
            1,
            [0.0, 10.0, 600.0, 40.0],
            ["1.", "", None, None, "24460967", "Jul-2024", "Jun-2026", "Under Investigation", "Assay", "Inspector", "Reply", "Remarks"],
        ),
        TableRow(1, [0.0, 40.0, 600.0, 60.0], [None, "Cefixime Tablets IP", None, None, None, None, None, None, None, None, None, None]),
        TableRow(1, [0.0, 60.0, 600.0, 80.0], [None, "(TAXIM-O 200)", None, None, None, None, None, None, None, None, None, None]),
    ]
    monkeypatch.setattr(spurious, "iter_table_rows", lambda _: rows)

    records = spurious.parse(path)

    assert len(records) == 1
    assert records[0]["drug_name"] == "Cefixime Tablets IP (TAXIM-O 200)"
    assert records[0]["batch_number"] == "24460967"
    assert records[0]["source_bbox"][3] == 80.0
    assert records[0]["parse_status"] == "PARSED"
