# Row-Extraction Evaluation

## Expanded unseen-document evaluation (October 2026)

Three additional May/April 2025 PDFs were acquired after the original parser work: one central NSQ, one state NSQ and one spurious publication. Their layouts were visually inspected before parser execution. Eleven rows were transcribed from rendered pages into `data/samples/ground_truth/unseen_may_2025_rows.jsonl` and then evaluated.

All 11 rows were reconstructed. Normalized match accuracy was 100% for product, batch, dates, finding, laboratory and available authority. Manufacturer normalized match accuracy was 81.8% overall: 100% for central NSQ, 60% for State NSQ and 100% for the spurious row. State NSQ differences involved punctuation/spacing/address reconstruction rather than missing manufacturer cells. After correcting wrong-field false-negative accounting on 19 October 2026, manufacturer precision, recall and F1 are each 0.818. A wrong nonempty value counts as both a false positive and a false negative. The earlier 1.000 recall and 0.900 F1 were incorrect.

This unseen set has primary manual review complete, remains small and awaits a second independent human review. It is reported separately from the original parser-seeded 77-row regression set.

## Evaluation Set

- Labelled rows: 77
- Central NSQ: 35
- State NSQ: 35
- Spurious: 6
- Revised alert: 1
- Parser version: `phase2-0.1.0`
- Original five-document corpus: 192 rows
- Expanded eight-document legacy corpus: 379 rows
- Matched labelled rows: 77

The frozen JSONL dataset is `data/samples/ground_truth/regulatory_rows.jsonl`. Each record retains document hash, filename, page, source row, bounding box and reconstructed source text.

## Validation Limitation

The initial labels were seeded from parser output and then checked against rendered PDF contact sheets. The reported 100% values therefore measure agreement of the frozen, visually reviewed subset with the current parser; they are **not** an independent blind estimate of generalization to unseen CDSCO layouts. This limitation is recorded to avoid an inflated accuracy claim. A future release should have a second reviewer transcribe a held-out set independently before using the numbers as production accuracy.

## Metrics by Field

Metrics are calculated only where the ground truth contains an applicable non-null value. This matters because central/state documents provide a testing laboratory, while spurious/revised documents provide a sample authority.

| Field | Labelled values | Exact | Normalized | Precision | Recall | F1 | Missing-field rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| Drug name | 77 | 100% | 100% | 100% | 100% | 100% | 0% |
| Batch number | 77 | 100% | 100% | 100% | 100% | 100% | 0% |
| Manufacturer | 77 | 100% | 100% | 100% | 100% | 100% | 0% |
| Manufacturing date | 77 | 100% | 100% | 100% | 100% | 100% | 0% |
| Expiry date | 77 | 100% | 100% | 100% | 100% | 100% | 0% |
| Failure reason | 77 | 100% | 100% | 100% | 100% | 100% | 0% |
| Testing laboratory | 70 | 100% | 100% | 100% | 100% | 100% | 0% |
| Sample authority | 7 | 100% | 100% | 100% | 100% | 100% | 0% |

## Metrics by Document Category

Every applicable field in the frozen set matched exactly and after normalization. Category sample sizes are uneven: revised-alert results contain only one record, and spurious results contain six. Those values demonstrate correct handling of the tested documents, not broad category coverage.

| Category | Labelled rows | Rows matched | Applicable field agreement |
|---|---:|---:|---:|
| Central NSQ | 35 | 35 | 100% |
| State NSQ | 35 | 35 | 100% |
| Spurious | 6 | 6 | 100% |
| Revised alert | 1 | 1 | 100% |

## Full-Corpus Parse Status

| Status | Rows |
|---|---:|
| `PARSED` | 360 |
| `PARTIAL` | 19 |
| `REQUIRES_REVIEW` | 0 |
| `FAILED` | 0 |

`PARTIAL` means the row was reconstructed with provenance, but at least one date value could not be normalized conservatively. It is not a regulatory-quality judgment.

## Common Extraction Errors

No false row splits or merged numbered rows remained after category-specific repair in the reviewed set. The observed risks were:

- product-name continuation rows in the June spurious layout;
- repeated table headers on later pages;
- embedded newlines and inconsistent whitespace;
- malformed or character-spaced dates;
- full day-month-year values in fields otherwise dominated by month-year values.

## Multi-line and Page-Break Findings

Multiline cells were retained within their row after whitespace normalization. Page headers were filtered by requiring a valid source serial. No reviewed row required merging content across two PDF pages. The current parser records page-local evidence and would require a new, tested strategy if a future row actually crosses a page boundary.

## Recommended Improvements

1. Produce an independently transcribed held-out set from additional months and have a second reviewer reconcile disagreements.
2. Add conservative normalization for explicitly supported full dates and character-spaced month names while retaining raw values.
3. Add layout-signature checks so an unexpected column structure becomes `REQUIRES_REVIEW`.
4. Store word-coordinate ranges alongside the current row bounding box in persistence.
5. Re-run field and category metrics whenever parser version or fixtures change.

The machine-readable evaluation output is generated at `data/interim/row_extraction_evaluation.json` and intentionally remains an intermediate artifact.
