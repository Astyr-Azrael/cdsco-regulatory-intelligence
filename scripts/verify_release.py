"""Reproduce the frozen corpus acceptance facts without live upstream requests."""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path
from sqlalchemy import func,select

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.app.database.models import SourceDocument,ParsedRegulatoryRecord,CanonicalManufacturer,CanonicalDrug,ManufacturerAlias,DrugAlias,EntityMatch
from backend.app.database.session import SessionLocal
from backend.app.api.routes.entities import _manufacturer_payload,_drug_payload
from backend.app.api.routes.batches import get_batch
from scripts.extract_regulatory_rows import extract_all
from scripts.evaluate_corpus_entities import evaluate
from backend.app.evaluation.row_extraction import evaluate_rows


def main():
    with SessionLocal() as db:
        sources=db.scalars(select(SourceDocument)).all()
        for source in sources:
            path=ROOT/source.local_raw_path
            if hashlib.sha256(path.read_bytes()).hexdigest()!=source.content_hash_sha256:
                raise ValueError(f"Source evidence changed: {path}")
        stats={"records":db.scalar(select(func.count(ParsedRegulatoryRecord.id))),"sources":len(sources),
               "canonical_manufacturers":db.scalar(select(func.count(CanonicalManufacturer.id))),
               "canonical_drugs":db.scalar(select(func.count(CanonicalDrug.id))),
               "manufacturer_mentions_linked":db.scalar(select(func.count(ManufacturerAlias.id))),
               "drug_mentions_linked":db.scalar(select(func.count(DrugAlias.id))),
               "unreviewed_candidates":db.scalar(select(func.count(EntityMatch.id)).where(EntityMatch.decision=="REVIEW",EntityMatch.review_status=="UNREVIEWED")),
               "primary_review_decisions":db.scalar(select(func.count(EntityMatch.id)).where(EntityMatch.review_status=="PRIMARY_SOURCE_REVIEW"))}
        histories=0
        for model,payload in ((CanonicalManufacturer,_manufacturer_payload),(CanonicalDrug,_drug_payload)):
            for entity in db.scalars(select(model)):
                dates=[r["provenance"]["publication_date"] or "9999" for r in payload(db,entity)["records"]]
                if dates!=sorted(dates): raise ValueError("History is not chronological")
                histories+=1
        batch=get_batch("TST2301",db)
        assert batch["total"]==5 and len(batch["contexts"])==5 and batch["ambiguous"]
        corpus=[{"id":s.id,"title":s.alert_title,"sha256":s.content_hash_sha256,"local_raw_path":s.local_raw_path,"source_system":s.source_system,"official_url":s.document_url,"date":s.publication_date,"rows":len(s.records)} for s in sources]
    extracted=extract_all()
    stored=[json.loads(x) for x in (ROOT/"data/interim/parsed_regulatory_records.jsonl").read_text(encoding="utf-8").splitlines() if x]
    assert extracted==stored
    truth=[json.loads(x) for x in (ROOT/"data/samples/ground_truth/unseen_may_2025_rows.jsonl").read_text(encoding="utf-8").splitlines() if x]
    report={"release_date":"2026-10-19","stats":stats,"corpus":corpus,"checks":{"raw_hashes_match":len(sources),"chronological_histories":histories,"batch_collision_contexts":len(batch["contexts"]),"legacy_extraction_reproduced":len(extracted)},
            "unseen_extraction":evaluate_rows(truth,extracted),"entity_evaluation":evaluate(),
            "limitations":["Primary assistant annotations only; independent human review pending","Small candidate-enriched entity benchmark","PostgreSQL and Docker execution not tested","No public HTTPS deployment"]}
    output=ROOT/"docs/release-verification.json"
    output.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({"stats":stats,"checks":report["checks"],"report":str(output)},indent=2))


if __name__=="__main__": main()
