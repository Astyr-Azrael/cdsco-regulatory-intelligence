"""Evaluate actual corpus annotations with coverage and explicit leakage boundaries."""
from __future__ import annotations
import json
import sys
from pathlib import Path
from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.database.models import ManufacturerAlias, DrugAlias
from backend.app.database.session import SessionLocal
from backend.app.entity_resolution.candidate_generation import generate_candidate_pairs
from backend.app.entity_resolution.string_similarity import similarity_features
from backend.app.entity_resolution.resolver import resolve_candidate
from backend.app.preprocessing.manufacturer_normalization import manufacturer_parts
from backend.app.preprocessing.drug_normalization import drug_parts, compatible_products


def metrics(rows):
    rows = [r for r in rows if r["label"] != "AMBIGUOUS"]
    tp=sum(r["label"]=="MATCH" and r["predicted"] for r in rows)
    fp=sum(r["label"]!="MATCH" and r["predicted"] for r in rows)
    fn=sum(r["label"]=="MATCH" and not r["predicted"] for r in rows)
    tn=sum(r["label"]!="MATCH" and not r["predicted"] for r in rows)
    precision=tp/(tp+fp) if tp+fp else None
    recall=tp/(tp+fn) if tp+fn else None
    f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None
    return {"pairs":len(rows),"tp":tp,"fp":fp,"fn":fn,"tn":tn,"precision":precision,"recall":recall,"f1":f1}


def evaluate():
    labels=[json.loads(x) for x in (ROOT/"data/samples/entity_resolution/corpus_pairs.jsonl").read_text(encoding="utf-8").splitlines() if x]
    report={"annotation_scope":"Primary assistant source-text review; no independent human sign-off. Candidate-enriched sample, not a random corpus estimate.",
            "review_boundary":"Applied decisions are regression only. Held-out subset was not applied as merge decisions. No threshold tuning after this fixture.",
            "labels":len(labels),"by_entity_type":{}}
    with SessionLocal() as db:
        for kind, alias_model, parts in (("MANUFACTURER",ManufacturerAlias,manufacturer_parts),("DRUG",DrugAlias,drug_parts)):
            aliases=db.scalars(select(alias_model)).all()
            items={}
            for a in aliases:
                p=parts(a.source_mention); items[p["normalized_name"]]=p
            candidates={tuple(sorted((a["normalized_name"],b["normalized_name"]))) for a,b in generate_candidate_pairs(list(items.values()))}
            methods={"normalized_equality":[],"rapidfuzz_proposal":[],"deployed_clusters":[]}
            blocked_positive=positives=0
            for row in (r for r in labels if r["entity_type"]==kind):
                left,right=parts(row["left"]),parts(row["right"])
                a,b=left["normalized_name"],right["normalized_name"]
                if row["label"]=="MATCH":
                    positives+=1
                    blocked_positive+=a==b or tuple(sorted((a,b))) in candidates
                compatible=(bool(left["normalized_address"] and right["normalized_address"]) and similarity_features(left["normalized_address"],right["normalized_address"])["token_set_ratio"]>=70) if kind=="MANUFACTURER" else compatible_products(left,right)
                proposal=resolve_candidate(similarity_features(a,b),96 if kind=="MANUFACTURER" else 98,compatible_context=compatible)["decision"]=="MATCH"
                left_ids={x.entity_id for x in aliases if x.normalized_mention==a}
                right_ids={x.entity_id for x in aliases if x.normalized_mention==b}
                for name,predicted in (("normalized_equality",a==b),("rapidfuzz_proposal",proposal),("deployed_clusters",bool(left_ids & right_ids))):
                    methods[name].append({"pair_id":row["pair_id"],"label":row["label"],"predicted":predicted,"usage":row["usage"]})
            report["by_entity_type"][kind]={"candidate_positive_coverage":blocked_positive/positives if positives else None,
                "candidate_positive_count":positives,
                "methods":{name:{"all_pairs":metrics(values),"held_out":metrics([r for r in values if r["usage"]=="HELD_OUT_OF_REVIEW_APPLICATION"]),"outcomes":values} for name,values in methods.items()}}
    return report


if __name__=="__main__":
    report=evaluate()
    path=ROOT/"data/interim/corpus_entity_evaluation.json"
    path.write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))
