# Final Stabilization Record

19 October 2026. Feature development is frozen for the bounded local academic demonstration.

## Corrections completed

| Audit issue | Final behavior |
|---|---|
| Unordered entity histories | Date, source, serial and ID ordering verified for all 904 profiles |
| Global batch assumption | Every product/manufacturer/site context is shown; TST2301 has five contexts |
| Fuzzy candidates never applied | Versioned primary source decisions apply 11 accepted links and retain six rejections |
| Unknown manufacturer entity | Twelve placeholder mentions remain raw values without identity links |
| Similarity presented as certainty | Equality and review states are explicit; score is not confidence |
| Decimal and concentration key loss | Product keys preserve decimal points and denominators |
| Incorrect extraction recall | Wrong nonempty fields count as both FP and FN |
| Tiny perfect entity fixture only | Forty corpus annotations added with source evidence, ambiguity and review/held-out boundaries |
| Node 16 build failure | Supported engines declared and Node runtime helper added |
| Docker frontend copy path | Corrected to /dist, matching the Vite configuration |
| Current portal required live access to restore | Offline frozen snapshot restore added |
| Contradictory handbook | Replaced with current operating, identity and evaluation semantics |
| Unreproducible final state | Source release commit and local evidence/database submission bundle created |

## Verification executed

- Backend suite: 33 passed, one optional live test skipped. The remaining warning is a Starlette/httpx deprecation notice.
- Frontend helper build: passed using bundled Node v24.19.0.
- Fresh offline database: 379 legacy plus 220 portal rows, 399 manufacturer clusters and 505 product clusters reproduced.
- Second portal restore: unchanged, no extra rows.
- Clean SQLite Alembic upgrade: revision 20261004_0001 reached.
- Browser: all five TST2301 contexts displayed, Martin and Brown profile shows twenty records and source rationale, portal dates show reporting month.
- Raw PDF extraction: 379 rows identical to preserved JSONL.
- All nine source hashes matched preserved files.
- Entity rebuild repeated on a database copy: decisions and counts stable.
- Word report: thirteen pages rendered through installed Microsoft Word and inspected. Packaged LibreOffice renderer was unavailable; no PDF is part of the requested document delivery.

## Final facts and disclosed limits

There are 599 source rows, nine source documents/snapshots, 399 organization clusters, 505 product clusters, 17 primary assistant source review decisions and 348 unreviewed suggestions. The original 16 entity pairs remain tuned regression examples; the additional forty contain 37 binary labels and three ambiguous examples.

Primary review is not independent human review. Applied-review metrics are regression results. Held-out product proposal recall is 0.167, and held-out fuzzy positives remain unmerged in deployed clusters. Company clusters do not establish legal or manufacturing-site identity. These are explicit validation and scope limits.

PostgreSQL, Docker execution and public HTTPS remain untested or undeployed. They are not required for running the frozen SQLite demonstration. Independent human review and broader evaluation remain future validation work.

## Files to read and run

- Word explanation: docs/project-report/CDSCO_Implementation_and_Method_Selection_Report.docx
- Technical handbook: docs/COMPLETE_PROJECT_DOCUMENTATION.md
- Machine verification: docs/release-verification.json
- Submission archive: releases/CDSCO_Final_Local_Demo_2026-10-19.zip
- Start backend: backend/.venv/Scripts/python.exe -m uvicorn backend.app.main:app --reload
- Start frontend: powershell -ExecutionPolicy Bypass -File scripts/frontend.ps1 dev
