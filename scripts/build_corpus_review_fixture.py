"""Materialize explicitly annotated real corpus pairs with immutable provenance.

Labels below are a primary assistant source-text review, not independent human
ground truth. Freeze this file before rerunning evaluations; do not tune to it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.database.session import SessionLocal
from backend.app.database.models import ParsedRegulatoryRecord
from backend.app.preprocessing.manufacturer_normalization import manufacturer_parts
from backend.app.preprocessing.drug_normalization import drug_parts

# kind, left observed name, right observed name, label, reason, apply decision
PAIRS = [
("MANUFACTURER","M/s.Martin & brown bio-sciences pvt. Ltd","M/s. Martin & Brown Bio Sciences","MATCH","Distinctive name and matching K No 918/419 Baddi site; omitted corporate suffix.",True),
("MANUFACTURER","M/s.Daffohils Laboratories Pvt Ltd","Daffohils Laboratoies Pvt. Ltd","MATCH","One missing r in Laboratories; same observed address.",True),
("MANUFACTURER","Jaineka Healthcare Pvt. Ltd","Jineka Healthcare Pvt. Ltd","MATCH","One vowel variation and identical address.",True),
("MANUFACTURER","M/s. Paksons Pharmaceuticals Private Limited","M/s. Paksons Pharmaceuticals Private Limitated","MATCH","Corporate suffix extraction error and identical address.",True),
("MANUFACTURER","M/s.Healers Lab Unit II","Healer's Lab Unit II","MATCH","Same explicitly named Unit II and same address.",True),
("MANUFACTURER","M/s. ABOD Pharmaceuticals","Abod Pharmaceutical","MATCH","Plural ending variation and same distinctive name and address.",True),
("MANUFACTURER","M/s. Puniska Injectables Pvt. Ltd","M/s. Puniska lnjectables Pvt.Ltd","MATCH","Lowercase l versus uppercase I extraction difference and same address.",True),
("MANUFACTURER","East African (India) Overseas","East African (India) Oversease","MATCH","Trailing e difference in same distinctive organization; address wording corroborates.",False),
("MANUFACTURER","Shervotech Pharmaceuticals","Shervotec Pharmaceuticals","MATCH","Trailing h variation and closely matching address.",False),
("MANUFACTURER","Pure & Cure Heatlhcare Pvt. Ltd","Pure and Cure Healthcare Pvt. Ltd","MATCH","Transposed letters in Healthcare; same named company and matching site wording.",False),
("MANUFACTURER","Agron Remedies Pvt. Ltd","M/s. Corona Remedies Pvt Ltd","NO_MATCH","Different distinctive company names and different source addresses.",True),
("MANUFACTURER","M/s. ZRS Pharmaceuticals India Pvt. Ltd","Lifecom Pharmaceuticals (India) Pvt. Ltd","NO_MATCH","Different distinctive company names and addresses.",True),
("MANUFACTURER","SGS Formulation Pvt Ltd","M/s.JMM Formulation Pvt. Ltd","NO_MATCH","Different company initials and addresses.",False),
("MANUFACTURER","Gats Biotech Pvt. Ltd","Aagya Biotech Pvt. Ltd","NO_MATCH","Different distinctive names and addresses.",False),
("MANUFACTURER","M/s.Helax Healthcare Private Limited","M/s HBC Healthcare Pvt.Ltd","NO_MATCH","Different distinctive company names and addresses.",False),
("MANUFACTURER","M/s.Apple Formulations Pvt. Ltd","Super Formulations Pvt. Ltd","NO_MATCH","Different distinctive company names and addresses.",False),
("MANUFACTURER","M/s. Kantil Pharmaceuticals Pvt. Ltd","Daxin Pharmaceuticals Pvt. Ltd","NO_MATCH","Different distinctive names and addresses.",False),
("MANUFACTURER","M/s. Nest Healthcare Pvt Ltd","Jineka Healthcare Pvt. Ltd","NO_MATCH","Different company names; similar suffix is insufficient.",False),
("MANUFACTURER","M/s. McW Healthcare (P) Ltd","M/s HBC Healthcare Pvt.Ltd","NO_MATCH","Different company names and source addresses.",False),
("MANUFACTURER","Oscar Remedies Pvt. Ltd","Agron Remedies Pvt. Ltd","NO_MATCH","Different company names and addresses.",False),
("DRUG","Calcium Aspartate, Calcium Orotate, Calcitriol Minerals And Vitamin Tablets","Calcium Aspartate, Calcium Orotate, Calcitriol, Minerals and Vitamins Tablets","MATCH","Same listed ingredients and form; plural and punctuation variation. No strength available on either mention.",False),
("DRUG","Telmisartan and Hydrochlorothizide Tablets I.P (40mg/12.5mg)","Telmisartan and Hydrochlorothiazide Tablets I.P (40mg/12.5 mg)","MATCH","Single missing a in salt name; both 40mg/12.5mg tablets.",True),
("DRUG","Mefenaic acid and paracetamol Suspension","Mefenamic Acid & Paracetamol Suspension","MATCH","Single missing m in ingredient; same combination and suspension form; strength unspecified on both.",True),
("DRUG","Calcium and Vitamin D3 Tablets IP","Calc ium and Vitamin D3 Tablets IP","MATCH","Space introduced within Calcium; same wording otherwise.",True),
("DRUG","Diclofenac Potass um & Serratiopeptidase Tablets","Diclofenac Potassium, & Serratiopeptidase Tablets","MATCH","Space introduced within Potassium; same combination and form.",True),
("DRUG","Amoxicillin and Potassium Clavulanate Tablets IP","Amoxicillin & Potassium Clavulanate Tablets","MATCH","Same listed salts and tablets; pharmacopoeia omitted on one mention; unspecified strengths on both.",False),
("DRUG","Compound Sodium Lactate Injection I.P","Compound Sodium Lactate Injection IP RL","MATCH","Same compound and form; RL is the source abbreviation. No strength stated on either.",False),
("DRUG","Itraconazole Capsules IP 200 mg","Itraconazole Capsules 200 mg","MATCH","Same salt form and 200mg strength; pharmacopoeia omitted on one mention.",False),
("DRUG","Sodium Chloride Injection IP 0.9% w/v (NS)","Sodium Chloride InjectionIP0.9% w/v (NS)","MATCH","Missing spaces at Injection IP; same 0.9 percent concentration and NS wording.",False),
("DRUG","Oral Rehydration Salts IP","ORS (Oral Rehydration Salts IP)","MATCH","Expanded name explicitly present on both mentions; ORS abbreviation added.",False),
("DRUG","Rosuvas F 10 Tablets Rosuvastatin and Fenofibrate Tablets IP","Rosuvas F 20 Tablets Rosuvastatin and Fenofibrate Tablets IP","NO_MATCH","Different product numbers 10 and 20; strength equivalence cannot be established.",True),
("DRUG","Paracetamol Tablets IP 500 mg","Paracetamol Tablets IP 650 mg","NO_MATCH","Different strengths 500mg and 650mg.",True),
("DRUG","Metronidazole Tablets IP 400mg","Metronidazole Tablets IP 200mg","NO_MATCH","Different strengths 400mg and 200mg.",True),
("DRUG","Itraconazole Capsules 200 mg","Itraconazole Capsules 100 mg","NO_MATCH","Different strengths 200mg and 100mg.",False),
("DRUG","Olagress MD 2.5","Olagress MD 5","NO_MATCH","Different numeric formulation wording; no evidence of identity.",True),
("DRUG","Pantoprazole For Injection I.P. 40 mg","Pantoprazole for Injection BP 40 mg","NO_MATCH","Different explicitly stated pharmacopoeia standard; retain distinct product wording.",False),
("DRUG","Sodium Polystyrene Sulfonate EP","Sodium Polystyrene Sulfonate BP","NO_MATCH","Different explicitly stated pharmacopoeia standard.",False),
("DRUG","Loperamide Hydrochloride Tablets I.P","Loperamide Hydrochloride Tablets IP 2 mg","NO_MATCH","Strength unspecified versus 2mg; insufficient evidence to assert formulation identity.",False),
("DRUG","Zinc Sulphate Dispersible Tablets IP","Zinc Sulphate Dispersible Tablets IP 20mg","NO_MATCH","Strength unspecified versus 20mg; keep unresolved product wording.",False),
("DRUG","Gentamicin Injection IP","Gentamicin Injection IP- 2ML","NO_MATCH","Pack volume unspecified versus 2ml; identity not established.",False),
]


def main():
    output = ROOT / "data/samples/entity_resolution"
    with SessionLocal() as db:
        records = db.scalars(select(ParsedRegulatoryRecord)).all()
        rows, decisions = [], []
        for index, (kind, left, right, label, reason, apply) in enumerate(PAIRS, 1):
            parts = manufacturer_parts if kind == "MANUFACTURER" else drug_parts
            evidence, full = [], []
            for mention in (left, right):
                key = parts(mention)["normalized_name"]
                candidates = [r for r in records if parts((r.raw_manufacturer if kind=="MANUFACTURER" else r.raw_drug_name) or "")["normalized_name"] == key]
                if not candidates:
                    raise ValueError(f"No source evidence for {mention}")
                record = max(candidates, key=lambda r: len((r.raw_manufacturer if kind=="MANUFACTURER" else r.raw_drug_name) or ""))
                raw = record.raw_manufacturer if kind=="MANUFACTURER" else record.raw_drug_name
                full.append(raw)
                evidence.append({"sha256": record.source_document.content_hash_sha256, "source_row": record.source_row, "source_page": record.source_page, "source_mention": raw, "official_url": record.source_document.document_url})
            if index in (38,39,40): label = "AMBIGUOUS"
            row = {"pair_id": f"corpus-{index:02d}", "entity_type": kind, "left": full[0], "right": full[1], "label": label,
                   "reason": reason, "reviewer": "CODEX_PRIMARY_SOURCE_TEXT_REVIEW", "review_status": "PRIMARY_REVIEW_ONLY",
                   "independent_human_review": False, "source_evidence": evidence,
                   "usage": "APPLIED_REVIEW_REGRESSION" if apply else "HELD_OUT_OF_REVIEW_APPLICATION"}
            rows.append(row)
            if apply:
                decisions.append({"decision_id": row["pair_id"], "entity_type": kind, "left": full[0], "right": full[1], "decision": label,
                                  "reason": reason, "reviewer": row["reviewer"], "reviewed_at": "2026-10-19",
                                  "independent_human_review": False, "source_evidence": evidence})
    for name, values in (("corpus_pairs.jsonl", rows), ("review_decisions.jsonl", decisions)):
        path = output / name
        if path.exists():
            raise FileExistsError(f"Frozen evidence already exists: {path}")
        path.write_text("".join(json.dumps(row, ensure_ascii=False)+"\n" for row in values), encoding="utf-8")
    print(json.dumps({"labelled_pairs": len(rows), "applied_decisions": len(decisions), "held_out_pairs": sum(not x[-1] for x in PAIRS)}, indent=2))


if __name__ == "__main__":
    main()
