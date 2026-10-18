"""Build conservative canonical entities and evaluate the RapidFuzz baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from sqlalchemy import delete, select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database.models import CanonicalDrug, CanonicalManufacturer, DrugAlias, EntityMatch, ManufacturerAlias, ParsedRegulatoryRecord
from backend.app.database.session import SessionLocal, create_database
from backend.app.entity_resolution.candidate_generation import generate_candidate_pairs
from backend.app.entity_resolution.evaluation import pairwise_metrics
from backend.app.entity_resolution.resolver import resolve_candidate
from backend.app.entity_resolution.string_similarity import similarity_features
from backend.app.entity_resolution.review import apply_reviews
from backend.app.preprocessing.drug_normalization import drug_parts, compatible_products
from backend.app.preprocessing.manufacturer_normalization import manufacturer_parts, normalize_address


def _preferred(values: list[str]) -> str:
    counts = Counter(" ".join(value.split()).strip(" ,.;") for value in values if value)
    return sorted(counts, key=lambda value: (-counts[value], len(value), value.casefold()))[0]


def _pair_key(entity_type: str, left: str, right: str) -> str:
    joined = "\0".join(sorted((left, right)))
    return hashlib.sha256(f"{entity_type}\0{joined}".encode()).hexdigest()


def _upsert_match(db, *, entity_type: str, left: dict, right: dict, decision: dict, evidence: dict) -> None:
    key = _pair_key(entity_type, left["normalized_name"], right["normalized_name"])
    match = db.scalar(select(EntityMatch).where(EntityMatch.entity_type == entity_type, EntityMatch.pair_key == key))
    values = {"left_mention": left["display_name"], "right_mention": right["display_name"], "left_normalized": left["normalized_name"], "right_normalized": right["normalized_name"], "match_method": "RAPIDFUZZ_BASELINE", "match_score": decision["score"], "decision": decision["decision"], "review_status": "UNREVIEWED", "evidence": evidence}
    if match is None:
        db.add(EntityMatch(entity_type=entity_type, pair_key=key, **values))
    else:
        if match.review_status == "UNREVIEWED":
            for field, value in values.items(): setattr(match, field, value)


def build_entities() -> dict:
    create_database()
    with SessionLocal() as db:
        # Rebuild only unreviewed derived candidates; preserve any human decisions.
        db.execute(delete(EntityMatch).where(EntityMatch.review_status == "UNREVIEWED"))
        records = db.scalars(select(ParsedRegulatoryRecord).order_by(ParsedRegulatoryRecord.id)).all()
        manufacturer_groups, drug_groups = defaultdict(list), defaultdict(list)
        for record in records:
            if record.raw_manufacturer and record.raw_manufacturer.strip().casefold() not in {"under investigation", "not mentioned", "not known", "unknown", "n/a"}:
                parts = manufacturer_parts(record.raw_manufacturer, record.raw_manufacturer_address)
                if parts["normalized_name"]: manufacturer_groups[parts["normalized_name"]].append((record, parts))
            if record.raw_drug_name:
                parts = drug_parts(record.raw_drug_name)
                if parts["normalized_name"]: drug_groups[parts["normalized_name"]].append((record, parts))

        for normalized, mentions in manufacturer_groups.items():
            entity = db.scalar(select(CanonicalManufacturer).where(CanonicalManufacturer.normalized_name == normalized))
            names = [parts["display_name"] for _, parts in mentions]
            if entity is None:
                entity = CanonicalManufacturer(canonical_name=_preferred(names), normalized_name=normalized, resolution_status="NORMALIZATION_EXACT")
                db.add(entity); db.flush()
            else: entity.canonical_name = _preferred(names)
            for record, parts in mentions:
                alias = db.scalar(select(ManufacturerAlias).where(ManufacturerAlias.source_record_id == record.id))
                entity.resolution_status = "NORMALIZATION_CLUSTER"
                values = {"entity_id": entity.id, "source_mention": record.raw_manufacturer, "display_name": parts["display_name"], "normalized_mention": normalized, "source_address": parts["address"], "normalized_address": parts["normalized_address"], "match_method": "NORMALIZATION_EXACT", "match_score": 100.0, "review_status": "NAME_EQUALITY_ONLY"}
                if alias is None: db.add(ManufacturerAlias(source_record_id=record.id, **values))
                else:
                    for field, value in values.items(): setattr(alias, field, value)

        for normalized, mentions in drug_groups.items():
            entity = db.scalar(select(CanonicalDrug).where(CanonicalDrug.normalized_name == normalized))
            names = [parts["display_name"] for _, parts in mentions]
            strengths = sorted({value for _, parts in mentions for value in parts["strengths"]})
            forms = sorted({value for _, parts in mentions for value in parts["dosage_forms"]})
            if entity is None:
                entity = CanonicalDrug(canonical_name=_preferred(names), normalized_name=normalized, strengths=strengths, dosage_forms=forms, resolution_status="NORMALIZATION_EXACT")
                db.add(entity); db.flush()
            else: entity.canonical_name, entity.strengths, entity.dosage_forms = _preferred(names), strengths, forms
            for record, parts in mentions:
                alias = db.scalar(select(DrugAlias).where(DrugAlias.source_record_id == record.id))
                entity.resolution_status = "NORMALIZATION_CLUSTER"
                values = {"entity_id": entity.id, "source_mention": record.raw_drug_name, "normalized_mention": normalized, "strengths": list(parts["strengths"]), "dosage_forms": list(parts["dosage_forms"]), "match_method": "NORMALIZATION_EXACT", "match_score": 100.0, "review_status": "NAME_EQUALITY_ONLY"}
                if alias is None: db.add(DrugAlias(source_record_id=record.id, **values))
                else:
                    for field, value in values.items(): setattr(alias, field, value)

        manufacturer_items = []
        for normalized, mentions in manufacturer_groups.items():
            addresses = [parts["normalized_address"] for _, parts in mentions if parts["normalized_address"]]
            manufacturer_items.append({"normalized_name": normalized, "display_name": _preferred([p["display_name"] for _, p in mentions]), "normalized_address": _preferred(addresses) if addresses else None})
        for left, right in generate_candidate_pairs(manufacturer_items):
            features = similarity_features(left["normalized_name"], right["normalized_name"])
            address_score = similarity_features(left.get("normalized_address") or "", right.get("normalized_address") or "")["token_set_ratio"]
            decision = resolve_candidate(features, 96.0, review_threshold=86.0, compatible_context=address_score >= 70.0)
            if decision["decision"] == "MATCH": decision["decision"] = "REVIEW"
            _upsert_match(db, entity_type="MANUFACTURER", left=left, right=right, decision=decision, evidence={"name_features": features, "address_similarity": address_score})

        drug_items = []
        for normalized, mentions in drug_groups.items():
            first = mentions[0][1]
            drug_items.append({"normalized_name": normalized, "display_name": _preferred([p["display_name"] for _, p in mentions]), "strengths": list(first["strengths"]), "dosage_forms": list(first["dosage_forms"])})
        for left, right in generate_candidate_pairs(drug_items):
            features = similarity_features(left["normalized_name"], right["normalized_name"])
            compatible = compatible_products(left, right)
            decision = resolve_candidate(features, 98.0, review_threshold=90.0, compatible_context=compatible)
            if decision["decision"] == "MATCH": decision["decision"] = "REVIEW"
            _upsert_match(db, entity_type="DRUG", left=left, right=right, decision=decision, evidence={"name_features": features, "context_compatible": compatible})

        valid_ids = [r.id for mentions in manufacturer_groups.values() for r, _ in mentions]
        db.execute(delete(ManufacturerAlias).where(ManufacturerAlias.source_record_id.not_in(valid_ids)))
        db.flush()
        reviews = apply_reviews(db, PROJECT_ROOT / "data/samples/entity_resolution/review_decisions.jsonl")
        db.flush()
        db.execute(delete(CanonicalManufacturer).where(~CanonicalManufacturer.aliases.any()))
        db.execute(delete(CanonicalDrug).where(~CanonicalDrug.aliases.any()))
        db.commit()
        return {"records": len(records), "manufacturer_source_mentions": sum(map(len, manufacturer_groups.values())), "canonical_manufacturers": db.query(CanonicalManufacturer).count(), "drug_source_mentions": sum(map(len, drug_groups.values())), "canonical_drugs": db.query(CanonicalDrug).count(), "candidate_pairs": db.query(EntityMatch).count(), "reviews": reviews}


def evaluate_fixture(path: Path) -> dict:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    reports = {}
    for entity_type in ("MANUFACTURER", "DRUG"):
        subset = [row for row in rows if row["entity_type"] == entity_type]
        true_pairs, predicted_pairs, outcomes = set(), set(), []
        for index, row in enumerate(subset):
            if entity_type == "MANUFACTURER":
                left, right = manufacturer_parts(row["left"]), manufacturer_parts(row["right"])
                features = similarity_features(left["normalized_name"], right["normalized_name"])
                a_score = similarity_features(normalize_address(row.get("left_address")), normalize_address(row.get("right_address")))["token_set_ratio"]
                compatible = a_score >= 70 or not row.get("left_address") or not row.get("right_address")
                predicted = resolve_candidate(features, 96, review_threshold=86, compatible_context=compatible)["decision"] == "MATCH"
            else:
                left, right = drug_parts(row["left"]), drug_parts(row["right"])
                features = similarity_features(left["normalized_name"], right["normalized_name"])
                compatible = compatible_products(left, right)
                predicted = resolve_candidate(features, 98, review_threshold=90, compatible_context=compatible)["decision"] == "MATCH"
            pair = (entity_type, index)
            if row["label"] == "MATCH": true_pairs.add(pair)
            if predicted: predicted_pairs.add(pair)
            outcomes.append({"pair_id": row["pair_id"], "label": row["label"], "predicted": "MATCH" if predicted else "NO_MATCH"})
        reports[entity_type.lower()] = {"labelled_pairs": len(subset), **pairwise_metrics(true_pairs, predicted_pairs), "outcomes": outcomes}
    return reports


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", type=Path, default=PROJECT_ROOT / "data/samples/entity_resolution/entity_pairs.jsonl")
    parser.add_argument("--report-json", type=Path, default=PROJECT_ROOT / "data/interim/entity_resolution_evaluation.json")
    args = parser.parse_args()
    result = {"build": build_entities(), "evaluation": evaluate_fixture(args.labels)}
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__": raise SystemExit(main())
