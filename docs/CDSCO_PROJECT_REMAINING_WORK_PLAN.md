# CDSCO Final Stabilization and Feature Freeze

Release date 19 October 2026. This replaces the earlier remaining-work checklist for the bounded local demonstration.

## Implemented and verified

- [x] Preserved 599 regulatory source rows from eight PDFs and one portal snapshot.
- [x] Reproduced all 379 PDF rows from unchanged raw files.
- [x] Verified all nine stored source hashes against preserved bytes.
- [x] Retained raw wording, source coordinates, hashes and warnings.
- [x] Corrected wrong-field precision/recall counting and regenerated evaluation.
- [x] Preserved decimal strengths and concentration denominators in product keys.
- [x] Excluded unknown manufacturer placeholders from canonical identities.
- [x] Defined organization clusters separately from manufacturing-site observations.
- [x] Added forty real-corpus source-backed entity annotations with ambiguity labels.
- [x] Applied seventeen explicit primary source decisions and retained uncertainty.
- [x] Separated applied-review regression, proposal results and held-out results.
- [x] Verified twenty Martin and Brown records across PDF and portal sources.
- [x] Corrected chronological ordering for all 904 entity histories.
- [x] Replaced globally unique batch assumptions with context-specific histories.
- [x] Verified five distinct TST2301 product contexts.
- [x] Added actual-corpus API, review persistence, idempotency and metric tests.
- [x] Backend suite passes with 33 tests; one optional live-source test is skipped.
- [x] Frontend production build passes with bundled Node 24.
- [x] Declared supported Node engines, pinned plugin version and added runtime helper.
- [x] Corrected Docker frontend output copy path.
- [x] Added offline portal restore and reproducible release verification.
- [x] Updated handbook, architecture, evaluation and final written report.
- [x] Prepared Word report explaining achievements and method selection.

## Final evidence

| Measure | Value |
|---|---:|
| Source rows and official sources | 599 and 9 |
| Legacy and portal rows | 379 and 220 |
| Organization and product clusters | 399 and 505 |
| Linked manufacturer and product mentions | 587 and 599 |
| Primary review decisions | 17 |
| Unreviewed suggestions | 348 |
| Entity profiles checked for chronology | 904 |

## Declared external validation and future scope

- [ ] Independent human review of extraction and entity annotations.
- [ ] Broader random corpus evaluation and additional layouts.
- [ ] Live PostgreSQL and Docker execution on the deployment host.
- [ ] Public domain, TLS and production backups if public hosting is required.
- [ ] Evidence-supported revision relationships if appropriate sources become available.

These are not claimed complete. Feature development is frozen for the local mini-project demonstration. The release demonstrates conservative linking with disclosed recall limits; it does not claim complete real-world identity resolution or research-grade validation.
