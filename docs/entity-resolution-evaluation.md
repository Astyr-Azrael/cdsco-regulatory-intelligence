# Entity resolution evaluation

Updated 19 October 2026.

## Datasets and independence

The original 16 pairs are a tuned regression fixture. They still produce 1.000 precision/recall/F1 on both entity types and must not be used as a general accuracy claim.

The new corpus_pairs.jsonl contains 40 source-backed pairs: 20 manufacturer and 20 product annotations, including 20 MATCH, 17 NO_MATCH and three AMBIGUOUS labels. The final three ambiguous product annotations are excluded from binary metrics. NO_MATCH denotes separation under the documented linkage policy.

Seventeen annotations form the applied primary-review regression subset. Twenty-three are held out from applying review decisions, leaving 20 binary held-out pairs after ambiguity exclusion. The reviewer is explicitly CODEX_PRIMARY_SOURCE_TEXT_REVIEW. No independent human review or blind random sampling is claimed.

## Measured comparisons

| Entity type and method | Binary pairs | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Manufacturer normalized equality | 20 | 0 | 0 | 10 | 10 | undefined | 0.000 | 0.000 |
| Manufacturer RapidFuzz proposal | 20 | 9 | 0 | 1 | 10 | 1.000 | 0.900 | 0.947 |
| Manufacturer deployed reviewed clusters | 20 | 7 | 0 | 3 | 10 | 1.000 | 0.700 | 0.824 |
| Product normalized equality | 17 | 0 | 0 | 10 | 7 | undefined | 0.000 | 0.000 |
| Product RapidFuzz proposal | 17 | 5 | 0 | 5 | 7 | 1.000 | 0.500 | 0.667 |
| Product deployed reviewed clusters | 17 | 4 | 0 | 6 | 7 | 1.000 | 0.400 | 0.571 |

This is a difficult candidate-enriched sample of non-equal keys. Equality-only recall of zero is expected and does not imply all corpus clusters are useless. Deployed results include applied decisions and therefore measure regression behavior.

## Held out from review application

Manufacturer proposal precision/recall/F1 are 1.000/1.000/1.000 across eleven pairs (three positives). Product proposal precision/recall/F1 are 1.000/0.167/0.286 across nine binary pairs (six positives). Product recall is limited by strict thresholds and formulation constraints.

Deployed held-out positive recall is zero because these fuzzy positives remain unreviewed in the actual cluster layer. Their absence is an intentional conservative coverage limit. It must not be hidden by proposal or applied-review scores.

All twenty annotated positive pairs enter candidate blocks, but the sample was chosen from candidate suggestions. This is conditional coverage and cannot establish unbiased blocking recall.

## Corpus and review result

599 regulatory records remain unchanged. 587 manufacturer mentions map to 399 organization clusters; 12 placeholders are excluded from identities. All 599 product mentions map to 505 wording clusters. Seventeen primary source reviews create eleven accepted links and six explicit rejections. There are 348 remaining unreviewed suggestions.

The Martin and Brown profile combines twenty records across legacy and current sources, with name and address evidence retained. Partial recall, company/site ambiguity and unknown-strength product wording remain disclosed limitations.

## Reproduce

Run scripts/evaluate_corpus_entities.py. Machine-readable results are in data/interim/corpus_entity_evaluation.json and included in docs/release-verification.json. Independent human annotation, larger random samples and cluster-level evaluation remain future validation work.
