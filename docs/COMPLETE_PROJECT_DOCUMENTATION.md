# CDSCO Regulatory Intelligence Complete Project Documentation

Release scope: local B.Tech Honours Data Engineering mini-project demonstration, stabilized 19 October 2026.

## 1 Purpose and operating boundary

The project organizes authoritative CDSCO publications into searchable product and manufacturer histories while retaining the supporting regulatory row. The release contains a bounded sample of official publications, rather than complete CDSCO coverage. Its central contribution is acquisition, extraction, validation, provenance and conservative entity linking. It does not predict medicine safety.

The companion Word report in `docs/project-report/CDSCO_Implementation_and_Method_Selection_Report.docx` explains achievements, algorithms, alternatives, comparisons, evaluation and viva preparation. This handbook is the operational reference. `docs/release-verification.json` contains machine-reproduced release facts.

## 2 Verified corpus

| Measure | Final value |
|---|---:|
| Regulatory source rows | 599 |
| Official source documents and snapshots | 9 |
| Legacy PDFs | 8 |
| Reconstructed legacy rows | 379 |
| Current portal rows | 220 |
| PARSED records | 580 |
| PARTIAL records | 19 |
| Organization name clusters | 399 |
| Product wording clusters | 505 |
| Manufacturer mentions linked | 587 |
| Product mentions linked | 599 |
| Primary source review decisions | 17 |
| Unreviewed fuzzy suggestions | 348 |

Twelve manufacturer values such as Under Investigation and Not Mentioned are retained as source values but excluded from manufacturer identity clusters. Final counts differ from the earlier 409/509/366 snapshot because placeholder removal, decimal-sensitive product keys and source-review decisions changed the derived entity layer. Raw records were not removed.

The event distribution is 333 NSQ, 258 State NSQ, seven Spurious and one Revised Alert. Eight PDF publications cover April through June 2025 alert periods and May through July 2025 publication dates. The portal snapshot reports August 2026. Its month-start date is only an internal sorting representation; the UI shows YYYY-MM and the label Reporting month.

## 3 End to end processing

1. Read the public legacy index and retain its HTML bytes and SHA-256.
2. Select documents within explicit date and category limits.
3. Download a PDF, resolve only the audited same-host iframe wrapper, validate the PDF signature and preserve bytes under a hash-bearing filename.
4. Extract page-separated text and benchmark PyMuPDF coordinates against pdfplumber words and tables.
5. Reconstruct supported rows using category-specific layout rules.
6. Retain source hash, page, serial, bounding box, raw cells, reconstructed text, parse status and parser version.
7. Adapt and validate the structured portal JSON through a separate source adapter.
8. Load source documents, ingestion runs and parsed records idempotently.
9. Form normalized name clusters, generate blocked candidates and score string similarities.
10. Apply versioned source-review decisions, retaining rejected and unreviewed candidates.
11. Serve records, aliases, histories and analytics through FastAPI.
12. Present search, profiles, records and official provenance through React.

Acquisition and database updates remain administrative scripts. The application does not trigger scraping when a user searches.

## 4 Main implementation files

| Area | Implementation |
|---|---|
| Legacy index and metadata | backend/app/scraper/sources/cdsco_alert_index.py |
| Download safety and hashing | backend/app/scraper/download.py |
| Current public source | backend/app/scraper/sources/cdsco_current_nsq.py |
| Coordinate evidence | backend/app/extraction/pdf_words.py |
| Parser routing and layouts | backend/app/extraction/parsers/ |
| Normalization | backend/app/preprocessing/ |
| Candidate blocking and scores | backend/app/entity_resolution/ |
| Review application | backend/app/entity_resolution/review.py |
| Entity build | scripts/run_entity_resolution.py |
| Review evidence | data/samples/entity_resolution/review_decisions.jsonl |
| Database models and queries | backend/app/database/ |
| Entity and batch histories | backend/app/api/routes/entities.py and batches.py |
| Frontend API integration | frontend/src/api.js |
| Release acceptance checks | scripts/verify_release.py and backend/tests/integration/test_final_corpus.py |

## 5 Extraction strategy and safeguards

PyMuPDF preserves text, page boundaries and original word order with coordinates. pdfplumber table geometry reconstructs ruled cells. Central and State NSQ share the tested eight-column implementation; Spurious and Revised Alert have their own routed modules that reuse the supported ten/twelve-column table logic.

Unknown table column structures are skipped by the current category parsers. This means a silent coverage loss remains possible for a new layout. The release verifier establishes reproducibility on the eight frozen PDFs, not universal parser support. New layouts require source inspection, annotation and tests before ingestion.

Raw cell values preserve reconstructed text after conservative whitespace and Unicode cleanup. They are not byte-identical text transcriptions. Original PDF bytes remain the ultimate evidence. Source serials are unique within each tested publication; a new layout restarting serials on each page would require a different record key.

Dates are normalized conservatively. A useful reconstructed row can be PARTIAL when a date cannot be normalized. Parse status measures extraction completeness, not regulatory severity.

## 6 Entity definitions and review policy

A manufacturer entity is an organization name cluster. It is not a legal registry identity or one manufacturing facility. Addresses and units remain source observations. Different addresses under one organization name are visible and must not be read as one site.

A product entity is a product wording cluster retaining ingredient wording, strength, dosage form, concentration and explicit numeric signals. Products with unknown strengths remain incompletely specified. A common generic name is not evidence of clinical interchangeability.

Normalized equality handles case, punctuation, corporate suffixes and common unit spacing. Normalized name equality is labelled NAME_EQUALITY_ONLY. A score of 100 means equal comparison keys; it is not identity confidence.

Blocking uses distinctive tokens, prefixes and address/location terms. Blocks with more than 80 items are omitted to avoid low-information all-pairs expansion. RapidFuzz records ratio, WRatio, token sort and token set scores. The aggregate uses 0.45 WRatio, 0.35 token-set ratio and 0.20 ratio. Weights and thresholds are heuristics, not a learned probability model.

Manufacturer proposal thresholds are 96 for match and 86 for review. Product proposal thresholds are 98 and 90. Numeric conflicts, incompatible strengths/forms and explicitly different pharmacopoeia standards prevent automatic product match proposals. Proposals remain unreviewed until an explicit decision is supplied.

Versioned decisions bind both mentions to source SHA-256 and serial row, include a rationale and reviewer attribution, and are reapplied on every rebuild. MATCH moves aliases into one cluster; NO_MATCH preserves separation. The current 17 decisions comprise 11 accepted links and six rejections. They are a primary assistant source-text review, with no claimed independent human sign-off.

The Martin and Brown variants now share one profile with 20 records spanning both source systems. Unknown manufacturer placeholders are displayed without a canonical identity link.

## 7 Histories and batch contexts

Canonical profiles join aliases to source-backed regulatory records and sort by publication/reporting date, source document, serial and record ID. Missing dates sort last. The release verifies chronological ordering for all 904 manufacturer/product profiles.

The portal supplies reporting month rather than a verified publication day. A month-level observation must not be described as a day-level event. Legacy release dates remain publication dates.

Batch wording is not globally unique. The batch API groups occurrences by product, manufacturer and observed normalized site address. The UI shows every context and its records. TST2301 has five product contexts, all of which are displayed. Context grouping is conservative and can split equivalent address variants.

Revised Alert remains a separate regulatory category. No correction relationship is invented. The old temporal helper modules are unused scaffolding; operational histories are constructed by the entity and batch routes.

## 8 Data model and idempotency

Implemented tables are source_documents, ingestion_runs, parsed_regulatory_records, canonical_manufacturers, manufacturer_aliases, canonical_drugs, drug_aliases, entity_matches and web_usage_events.

Source content hashes are unique. Parsed rows are unique by source document and serial row for the tested corpus. Aliases link one source record to a cluster. Match records contain normalized mentions and review evidence; they do not contain foreign keys to canonical entities. Ingestion runs are process logs and have no source-document association table. Usage entity references are logical string references, not database foreign keys.

An unchanged portal hash does not duplicate database rows. Raw snapshot filenames include retrieval time, so repeated retrieval can preserve more than one identical JSON file; database source identity still uses the full hash. Changed snapshots are stored separately and may contain repeated real-world events. The current analytics count source rows, not deduplicated legal events.

Entity rebuilds reset deterministic links and then reapply all recorded decisions. Reviewed candidates survive regeneration. A pre-final database backup is retained locally in data/cdsco_demo.pre-final-20261019.db.

SQLite is the tested local store. SQLAlchemy and psycopg configuration support a PostgreSQL path, but a live PostgreSQL run remains unverified. Alembic creates the baseline schema; its initial revision currently imports model metadata and must be frozen or replaced with explicit migration operations before future schema evolution.

## 9 API and frontend

| Route | Purpose |
|---|---|
| GET /api/search | Paginated record search and filters |
| GET /api/events/{id} | Raw fields, entity links and provenance |
| GET /api/entities/search | Organization and product cluster search including aliases |
| GET /api/entities/manufacturers/{id} | Mentions, addresses, review decisions and history |
| GET /api/entities/drugs/{id} | Mentions, strength/form signals and history |
| GET /api/entities/review-queue | Paginated unresolved suggestions with true total count |
| GET /api/batches/{wording} | All observed batch contexts and records |
| GET /api/sources | Official source register |
| GET /api/analytics/summary | Descriptive regulatory corpus statistics |
| POST /api/usage/events | Anonymous session-based interaction logging |
| GET /api/usage/summary | Separate application usage aggregates |

Record search uses SQL substring matching. Entity search is also lexical and capped at 25 entities of each type. It is not semantic search. The search page displays at most the first 100 record matches; the API itself supports pagination.

React loads actual API responses, shows loading/empty/error states and never silently substitutes the six-record sample after an API failure. Company/product profiles identify clustering and primary review evidence. Official source links remain prominent.

Usage logging records search, zero result, filter, entity view, record view and source click events. Session IDs are hashed. Search text remains stored as submitted, so the deployment should define retention and access policies. Only a small number of development interactions exist; these are instrumentation checks, not user research.

## 10 Evaluation and interpretation

The original 77-row extraction fixture was parser-seeded and visually reviewed. It is a regression fixture. The later 11 rows were transcribed from three additional PDFs before parser execution and have primary review only.

All 11 unseen rows are located. Manufacturer normalized equality is 9/11, or 81.8 percent. Corrected precision, recall and F1 are all 0.818 for this field. A wrong nonempty value counts as both a false positive and a false negative. Product normalized equality is 100 percent, while exact product equality is 54.5 percent because whitespace and punctuation differ.

The original 16 entity pairs are retained as tuned regression examples. Forty additional real-corpus pairs include 20 MATCH, 17 NO_MATCH and three AMBIGUOUS annotations, each with immutable source references. Three ambiguous product pairs are excluded from binary metrics. Seventeen pairs are used for applied-review regression; 23 annotations are held out from review application.

On the complete candidate-enriched sample, the RapidFuzz proposal baseline has manufacturer precision 1.000, recall 0.900 and F1 0.947 across 20 binary pairs. Product proposal precision is 1.000, recall 0.500 and F1 0.667 across 17 binary pairs. These are small source-text annotations, not an unbiased corpus accuracy estimate.

The held-out proposal results are manufacturer 1.000/1.000/1.000 on 11 pairs and product 1.000/0.167/0.286 on nine binary pairs. The conservative deployed clusters leave held-out fuzzy positives unmerged, so their held-out positive recall is zero on this deliberately difficult sample. This is documented as a coverage limitation rather than hidden by the original fixture score.

All 20 annotated positive pairs entered candidate blocks, but the sample was drawn from candidates. That is a conditional coverage check, not global blocking recall.

## 11 Running the frozen local demo

Run from the repository root:

```powershell
backend\.venv\Scripts\python.exe scripts\run_entity_resolution.py
backend\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

In a second terminal, also from the root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\frontend.ps1 dev
```

The frontend helper uses a supported installed Node or the available Codex bundled Node. Node 16 is unsupported. Vite requires Node 20.19 or Node 22.12 and newer. Open http://127.0.0.1:5173.

For fresh Python setup, create backend/.venv and install requirements.txt. For frontend dependency setup run the frontend helper with install, which uses npm ci. On another computer, install the declared Node version rather than relying on the Codex bundle.

If port 8000 is occupied, inspect the listener before stopping the known API process. Do not start a second API on the same port.

## 12 Reproducing and verifying the corpus

Preserve raw files and intermediate metadata before using acquisition commands. The frozen submission bundle includes the working database and evidence, because raw/intermediate data are intentionally ignored by Git.

```powershell
backend\.venv\Scripts\python.exe scripts\load_database.py
backend\.venv\Scripts\python.exe scripts\run_entity_resolution.py
backend\.venv\Scripts\python.exe scripts\evaluate_corpus_entities.py
backend\.venv\Scripts\python.exe scripts\verify_release.py
backend\.venv\Scripts\python.exe -m pytest -q
powershell -ExecutionPolicy Bypass -File scripts\frontend.ps1 build
```

load_database.py loads only legacy rows. The included database also contains the preserved portal snapshot. To rebuild a missing database without a live request, use scripts/restore_portal_snapshot.py followed by run_entity_resolution.py.

verify_release.py re-extracts the eight PDFs, compares all 379 rows to the stored JSONL, validates all nine source hashes, checks every canonical history and confirms the five TST2301 contexts. It writes docs/release-verification.json.

Live ingestion uses process_documents.py with explicit --max-documents 8 --start-date 2025-01-01 --end-date 2025-12-31 and ingest_current_nsq.py. These are optional fresh acquisitions, not required for the frozen demonstration.

## 13 Deployment status

The backend and frontend Dockerfiles, PostgreSQL Compose service, startup migrations, CORS settings and Nginx proxy are configured. The frontend container copy path now matches Vite output at /dist.

SQLite tests and migration execution have been verified. Docker and PostgreSQL execution have not been verified on this machine. No public domain, TLS deployment or production backup service is claimed. See installation-and-deployment.md for the optional deployment procedure.

## 14 Submission demonstration and freeze

Show a source PDF row, its extracted record, a reviewed organization profile spanning PDF and portal records, a product history, the TST2301 collision, the unresolved suggestion queue and separate usage analytics. Finish by opening the official source and matching its local SHA-256.

Feature development is frozen for the bounded local demonstration. Future work is independent annotation review, broader corpus coverage and deployment validation. These are research/deployment extensions and must remain disclosed; no additional model is required for the current demonstration.
