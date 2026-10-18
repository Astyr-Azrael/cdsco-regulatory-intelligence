# Entity resolution methodology

Updated 19 October 2026. See COMPLETE_PROJECT_DOCUMENTATION.md sections 6 and 10 and project-report/final-report.md for the complete explanation.

## Identity scope

Manufacturer entities are organization name clusters. Different site addresses remain source observations; a cluster is not one factory or a legal registry confirmation. Placeholder values such as Under Investigation remain raw values and do not receive manufacturer identities.

Product entities group source wording while preserving decimal strengths, dosage form, concentration denominators, explicit numbers and pharmacopoeia wording. A product group does not establish clinical interchangeability.

## Candidate and score method

Normalize Unicode, casing, corporate abbreviations and spacing. Block by distinctive name tokens, prefix and location. Skip blocks above 80 members. Compute RapidFuzz ratio, WRatio, token sort and token set scores. Aggregate 0.45 WRatio + 0.35 token set + 0.20 ratio. These heuristic weights are not calibrated probabilities.

Manufacturer thresholds are match 96/review 86, with address compatibility at least 70 for a proposal. Product thresholds are 98/90 with numeric, strength, dosage-form and explicit standard compatibility. All fuzzy proposals remain unresolved until an explicit review decision is present.

## Operational source review

data/samples/entity_resolution/review_decisions.jsonl contains 17 primary source-text decisions: 11 MATCH and six NO_MATCH. Each contains both source hashes, serial rows, raw mentions, rationale, date and reviewer attribution. These are assistant primary reviews, not independently human-verified identities.

backend/app/entity_resolution/review.py validates that source evidence is present and unchanged, applies accepted links to aliases, retains rejections and reapplies decisions on every rebuild. A reviewed alias score remains a string comparison score. The API displays review rationale and the distinction between primary review and normalized equality.

Unknown candidates stay in the paginated GET /api/entities/review-queue. No unauthenticated public mutation endpoint was added. Future reviews are recorded in the versioned decision file, checked against the source and applied by the administrative entity-build script.

## Reproduction

Run scripts/run_entity_resolution.py, then scripts/evaluate_corpus_entities.py and scripts/verify_release.py. The final corpus has 399 organization clusters, 505 product clusters and 348 remaining review suggestions.

SentenceTransformer matching, custom NER and LLM extraction were not benchmarked or retained. No superiority over those models is claimed.
