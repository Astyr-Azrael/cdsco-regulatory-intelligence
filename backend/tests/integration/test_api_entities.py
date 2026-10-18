from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.app.database.models import Base, CanonicalDrug, CanonicalManufacturer, DrugAlias, ManufacturerAlias, ParsedRegulatoryRecord, SourceDocument
from backend.app.database.session import get_db
from backend.app.main import app


def test_entity_profiles_and_usage_are_provenance_backed():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        source = SourceDocument(source_system="TEST", source_url="https://example.test", document_url="https://example.test/source.pdf", alert_title="Fixture NSQ", alert_type="NSQ", publication_date="2026-01-01", original_filename="source.pdf", content_hash_sha256="a" * 64, extraction_status="ROW_EXTRACTED")
        db.add(source); db.flush()
        record = ParsedRegulatoryRecord(source_document_id=source.id, source_page=1, source_row=1, alert_type="NSQ", raw_drug_name="Example Tablets IP 40 mg", raw_batch_number="B1", raw_manufacturer="M/s Example Pvt. Ltd.", raw_row_text="fixture", parse_status="PARSED", parser_name="fixture", parser_version="1")
        db.add(record); db.flush()
        manufacturer = CanonicalManufacturer(canonical_name="Example Private Limited", normalized_name="example private limited", resolution_status="NORMALIZATION_EXACT")
        drug = CanonicalDrug(canonical_name="Example Tablets IP 40 mg", normalized_name="example tablets ip 40mg", strengths=["40mg"], dosage_forms=["tablets"], resolution_status="NORMALIZATION_EXACT")
        db.add_all([manufacturer, drug]); db.flush()
        db.add(ManufacturerAlias(entity_id=manufacturer.id, source_record_id=record.id, source_mention=record.raw_manufacturer, display_name="Example Pvt. Ltd.", normalized_mention=manufacturer.normalized_name, match_method="NORMALIZATION_EXACT", match_score=100, review_status="AUTO_ACCEPTED"))
        db.add(DrugAlias(entity_id=drug.id, source_record_id=record.id, source_mention=record.raw_drug_name, normalized_mention=drug.normalized_name, strengths=["40mg"], dosage_forms=["tablets"], match_method="NORMALIZATION_EXACT", match_score=100, review_status="AUTO_ACCEPTED"))
        db.commit()
        manufacturer_id = manufacturer.id

    def override_db():
        with Session(engine) as db:
            yield db

    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as client:
            search = client.get("/api/search", params={"q": "Example"})
            assert search.status_code == 200
            assert search.json()["items"][0]["canonical_manufacturer"]["id"] == manufacturer_id
            profile = client.get(f"/api/entities/manufacturers/{manufacturer_id}")
            assert profile.status_code == 200
            assert profile.json()["records"][0]["provenance"]["page"] == 1
            usage = client.post("/api/usage/events", json={"session_id": "anonymous-session", "event_type": "ENTITY_VIEWED", "entity_type": "MANUFACTURER", "entity_id": str(manufacturer_id)})
            assert usage.status_code == 202
            assert client.get("/api/usage/summary").json()["events"]["ENTITY_VIEWED"] == 1
    finally:
        app.dependency_overrides.clear()
