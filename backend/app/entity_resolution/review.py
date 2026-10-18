"""Apply versioned primary source reviews without changing raw regulatory rows."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from sqlalchemy import select

from backend.app.database.models import CanonicalDrug, CanonicalManufacturer, DrugAlias, EntityMatch, ManufacturerAlias, ParsedRegulatoryRecord
from backend.app.preprocessing.drug_normalization import drug_parts
from backend.app.preprocessing.manufacturer_normalization import manufacturer_parts
from backend.app.entity_resolution.string_similarity import aggregate_similarity, similarity_features


def pair_key(kind: str, left: str, right: str) -> str:
    joined = "\0".join(sorted((left, right)))
    return hashlib.sha256(f"{kind}\0{joined}".encode()).hexdigest()


def apply_reviews(db, path: Path) -> dict:
    """Reapply accepted decisions after every rebuild; rejection never merges."""
    if not path.exists():
        return {"decisions": 0, "merges": 0}
    decisions = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    merges = 0
    for item in decisions:
        kind = item["entity_type"]
        if kind not in {"MANUFACTURER", "DRUG"} or item["decision"] not in {"MATCH", "NO_MATCH"}:
            raise ValueError("Reviews require a valid entity type and explicit MATCH or NO_MATCH")
        if len(item["source_evidence"]) < 2 or not item.get("reason") or not item.get("reviewer"):
            raise ValueError("Reviews require two source references, a reason and reviewer attribution")
        alias_model, entity_model = (ManufacturerAlias, CanonicalManufacturer) if kind == "MANUFACTURER" else (DrugAlias, CanonicalDrug)
        parts = manufacturer_parts if kind == "MANUFACTURER" else drug_parts
        left_key, right_key = parts(item["left"])["normalized_name"], parts(item["right"])["normalized_name"]
        key = pair_key(kind, left_key, right_key)
        # Evidence is bound to immutable source hash and serial, not local DB IDs.
        for evidence in item["source_evidence"]:
            record = db.scalar(select(ParsedRegulatoryRecord).join(ParsedRegulatoryRecord.source_document).where(
                ParsedRegulatoryRecord.source_document.has(content_hash_sha256=evidence["sha256"]),
                ParsedRegulatoryRecord.source_row == evidence["source_row"],
            ))
            if record is None:
                raise ValueError(f"Review evidence not present for {item['decision_id']}")
            raw = record.raw_manufacturer if kind == "MANUFACTURER" else record.raw_drug_name
            if raw != evidence["source_mention"]:
                raise ValueError(f"Review evidence changed for {item['decision_id']}")
        match = db.scalar(select(EntityMatch).where(EntityMatch.entity_type == kind, EntityMatch.pair_key == key))
        if match is None:
            match = EntityMatch(entity_type=kind, pair_key=key, left_mention=item["left"], right_mention=item["right"], left_normalized=left_key, right_normalized=right_key, match_method="SOURCE_EVIDENCE_REVIEW", match_score=0)
            db.add(match)
        match.decision = item["decision"]
        match.match_score = aggregate_similarity(similarity_features(left_key,right_key))
        match.review_status = "PRIMARY_SOURCE_REVIEW"
        match.evidence = item
        if item["decision"] != "MATCH":
            continue
        aliases = db.scalars(select(alias_model).where(alias_model.normalized_mention.in_([left_key, right_key]))).all()
        ids = sorted({alias.entity_id for alias in aliases})
        if not ids:
            raise ValueError(f"No aliases for review {item['decision_id']}")
        if kind == "DRUG":
            a, b = drug_parts(item["left"]), drug_parts(item["right"])
            if a["strengths"] != b["strengths"] or a["dosage_forms"] != b["dosage_forms"]:
                raise ValueError("Reviewed product merge conflicts with strength or dosage form")
        target = db.get(entity_model, ids[0])
        target.resolution_status = "PRIMARY_SOURCE_REVIEW"
        all_aliases = db.scalars(select(alias_model).where(alias_model.entity_id.in_(ids))).all()
        for alias in all_aliases:
            alias.entity_id = target.id
            alias.match_method = "SOURCE_EVIDENCE_REVIEW"
            alias.match_score = min(alias.match_score, match.match_score)
            alias.review_status = "PRIMARY_SOURCE_REVIEW"
        merges += max(0, len(ids) - 1)
        db.flush()
    return {"decisions": len(decisions), "merges": merges}
