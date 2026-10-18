# CDSCO Regulatory Intelligence

Entity-Centric Drug Regulatory Intelligence from Fragmented CDSCO Alerts is an academic data-engineering project that reconstructs regulator-published drug records while preserving official-source provenance.

The working demo indexes 379 rows reconstructed from eight official CDSCO PDFs and 220 current NSQ records from an audited August 2026 public-portal snapshot. The interface and API expose record search, canonical product/manufacturer profiles with retained aliases, batch records, temporal histories, analytics and a source register.

The six-record frontend sample remains an offline regression fixture. The final local release includes 399 organization clusters, 505 product clusters, 17 primary source review decisions and 348 unresolved suggestions. Organization clusters preserve observed site addresses; they do not certify legal identities. See the 13-page Word report in docs/project-report/CDSCO_Implementation_and_Method_Selection_Report.docx for achievements, method comparisons and limitations.

## Run the complete demo

```powershell
cd C:\path\to\cdsco-regulatory-demo
backend\.venv\Scripts\python.exe scripts\load_database.py
backend\.venv\Scripts\python.exe scripts\restore_portal_snapshot.py
backend\.venv\Scripts\python.exe scripts\run_entity_resolution.py
backend\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

In a second PowerShell window:

```powershell
cd C:\path\to\cdsco-regulatory-demo
powershell -ExecutionPolicy Bypass -File scripts\frontend.ps1 dev
```

Open `http://127.0.0.1:5173`. Vite proxies `/api` to `http://127.0.0.1:8000`.

## Final release verification

Run from the root with the preserved evidence available:

```powershell
backend\.venv\Scripts\python.exe scripts\verify_release.py
backend\.venv\Scripts\python.exe -m pytest -q
powershell -ExecutionPolicy Bypass -File scripts\frontend.ps1 build
```

The suite passes 33 tests and skips one optional live test. Node 20.19 or 22.12 and newer is required; the helper also locates the bundled Node 24 runtime. PostgreSQL and Docker are configured but remain untested on this machine. The submission ZIP contains the frozen evidence and database that Git ignores.

## Phase 1 data pipeline

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/process_documents.py --max-documents 8 --start-date 2025-01-01 --end-date 2025-12-31
python scripts/benchmark_extraction.py
python scripts/extract_regulatory_rows.py
python scripts/evaluate_row_extraction.py
python scripts/load_database.py
python scripts/run_entity_resolution.py
python -m pytest -q
```

Run these commands from the repository root, not from inside `backend/`. Each pytest session uses a unique directory under `.pytest-runs/`, so it does not require access to the Windows user Temp directory or reuse a previously locked test directory.

Generated evidence is written to:

```text
data/raw/html/                         unchanged CDSCO index snapshot
data/raw/pdf/                          unchanged official PDFs
data/interim/cdsco_alert_records.jsonl
data/interim/cdsco_phase1_audit.json
data/interim/extraction_benchmark.json
data/interim/parsed_regulatory_records.jsonl
data/interim/row_extraction_evaluation.json
```

Raw and intermediate outputs are intentionally Git-ignored. The tracked tests use local fixtures; the live CDSCO smoke test is opt-in:

```powershell
$env:RUN_LIVE_CDSCO_TESTS="1"
python -m pytest backend/tests/integration/test_cdsco_live.py -q
```

## Current public NSQ portal

The observed public portal contract is documented in `docs/current-nsq-source-audit.md`. To make one bounded snapshot request, preserve the raw JSON and idempotently load its rows:

```powershell
backend\.venv\Scripts\python.exe scripts\ingest_current_nsq.py
```

The command validates the response shape and record count before persistence. A repeated unchanged response is detected by SHA-256 and is not duplicated.

## Database

The demo defaults to `sqlite:///./data/cdsco_demo.db` so it runs without external services. Set `DATABASE_URL` to the PostgreSQL URL in `.env.example` to use PostgreSQL. The implemented tables are:

```text
source_documents
ingestion_runs
parsed_regulatory_records
canonical_manufacturers
manufacturer_aliases
canonical_drugs
drug_aliases
entity_matches
web_usage_events
```

Raw cells, hashes, page/row/bounding-box evidence, parser version and parse status are retained. Entity clusters remain linked to source mentions; placeholder manufacturers have no identity link. Reviewed links are reapplied from source-bound decisions, and unreviewed fuzzy suggestions stay separate.

## Phase 2 reports

- [Complete project documentation](docs/COMPLETE_PROJECT_DOCUMENTATION.md) — architecture, pipeline, API, frontend, operation, testing and extension handbook
- `docs/extraction-benchmark.md`
- `docs/row-extraction-evaluation.md`
- `docs/current-nsq-source-audit.md`
- `docs/entity-resolution-methodology.md`
- `docs/entity-resolution-evaluation.md`
- `docs/architecture/final-architecture.md`
- `docs/installation-and-deployment.md`
- `docs/project-report/final-report.md`

The first 77-row ground-truth set was seeded from parser output and visually checked against rendered pages. Its 100% agreement result is not presented as an independent blind generalization estimate; the limitation and next validation step are documented in the evaluation report.

## Important interpretation rule

This project organizes information published by authorized regulators. It does not determine whether a medicine or manufacturer is safe or unsafe, and it does not provide medical advice.
