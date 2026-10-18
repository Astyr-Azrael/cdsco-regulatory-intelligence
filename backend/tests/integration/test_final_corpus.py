"""Read-only acceptance checks on the preserved corpus, skipped if not supplied."""
import hashlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from backend.app.database.models import CanonicalDrug, CanonicalManufacturer, SourceDocument
from backend.app.database.session import get_db
from backend.app.main import app

ROOT=Path(__file__).resolve().parents[3]


@pytest.fixture
def corpus_client():
    path=ROOT/"data/cdsco_demo.db"
    if not path.exists():
        pytest.skip("Preserved corpus database not supplied")
    import sqlite3
    engine=create_engine("sqlite://",creator=lambda:sqlite3.connect(path.as_uri()+"?mode=ro",uri=True,check_same_thread=False))
    def override():
        with Session(engine) as db:
            yield db
    app.dependency_overrides[get_db]=override
    with TestClient(app) as client:
        yield client,engine
    app.dependency_overrides.clear()
    engine.dispose()


def test_corpus_counts_and_all_raw_hashes(corpus_client):
    client,engine=corpus_client
    data=client.get("/api/analytics/summary").json()
    assert data["regulatory_records"]==599
    assert data["official_documents"]==9
    with Session(engine) as db:
        for source in db.scalars(select(SourceDocument)):
            assert hashlib.sha256((ROOT/source.local_raw_path).read_bytes()).hexdigest()==source.content_hash_sha256


def test_every_entity_history_is_chronological(corpus_client):
    client,engine=corpus_client
    with Session(engine) as db:
        for model,route in ((CanonicalManufacturer,"manufacturers"),(CanonicalDrug,"drugs")):
            for entity_id in db.scalars(select(model.id)):
                response=client.get(f"/api/entities/{route}/{entity_id}")
                assert response.status_code==200
                dates=[r["provenance"]["publication_date"] or "9999" for r in response.json()["records"]]
                assert dates==sorted(dates)


def test_reused_batch_is_not_one_product(corpus_client):
    client,_=corpus_client
    data=client.get("/api/batches/TST2301").json()
    assert data["total"]==5
    assert data["ambiguous"]
    assert len(data["contexts"])==5
    assert sum(c["total"] for c in data["contexts"])==5


def test_reviewed_martin_history_spans_both_sources(corpus_client):
    client,_=corpus_client
    entities=client.get("/api/entities/search",params={"q":"Martin"}).json()["manufacturers"]
    assert len(entities)==1
    data=client.get(f"/api/entities/manufacturers/{entities[0]['id']}").json()
    assert data["record_count"]==20
    assert data["resolution_status"]=="PRIMARY_SOURCE_REVIEW"
    assert {r["provenance"]["source_system"] for r in data["records"]}=={"CDSCO_LEGACY_PDF","CDSCO_CURRENT_NSQ_PORTAL"}


def test_entity_rebuild_preserves_decisions_and_is_idempotent(tmp_path,monkeypatch):
    import sqlite3
    import scripts.run_entity_resolution as runner
    from sqlalchemy.orm import sessionmaker
    source=ROOT/"data/cdsco_demo.db"
    if not source.exists(): pytest.skip("Preserved corpus database not supplied")
    copy=tmp_path/"copy.db"
    with sqlite3.connect(source) as src, sqlite3.connect(copy) as dst:
        src.backup(dst)
    engine=create_engine(f"sqlite:///{copy.as_posix()}")
    monkeypatch.setattr(runner,"SessionLocal",sessionmaker(engine))
    monkeypatch.setattr(runner,"create_database",lambda:None)
    first=runner.build_entities()
    second=runner.build_entities()
    assert first==second
    with Session(engine) as db:
        matches=db.execute(select(CanonicalManufacturer).where(CanonicalManufacturer.resolution_status=="PRIMARY_SOURCE_REVIEW")).scalars().all()
        assert len(matches)>=7
    engine.dispose()
