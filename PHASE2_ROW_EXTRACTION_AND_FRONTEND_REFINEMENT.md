# CDSCO Regulatory Intelligence — Phase 2

> Entity-Centric Drug Regulatory Intelligence from Fragmented CDSCO Alerts

This file records the Phase 2 implementation brief supplied for the project. The implementation follows this order:

```text
real CDSCO documents
  → layout-aware extraction
  → verified row reconstruction
  → measured extraction quality
  → structured persistence
  → real search
  → clean frontend
  → entity resolution later
```

## Implemented scope

- [x] Benchmark PyMuPDF text and coordinate extraction.
- [x] Benchmark pdfplumber words and tables on the same five PDFs.
- [x] Create `docs/extraction-benchmark.md` from measured results.
- [x] Preserve a 77-row visually reviewed ground-truth subset.
- [x] Add separate central NSQ, state NSQ, spurious and revised-alert parsers.
- [x] Preserve raw cells, raw row text, document hash, page, row and bounding box.
- [x] Use `PARSED`, `PARTIAL`, `REQUIRES_REVIEW` and `FAILED` status semantics.
- [x] Measure and document field-level extraction agreement.
- [x] Audit the current public NSQ portal without inventing endpoints or bypassing controls.
- [x] Add source-document, ingestion-run and parsed-record persistence.
- [x] Add real API search, filters, pagination, dynamic counts and source metadata.
- [x] Connect the frontend to persisted records with loading, empty and error states.
- [x] Retain the six-record sample as an offline regression fixture only.

## Deliberately deferred

The following remain outside Phase 2 because row extraction had to be validated first and entity-resolution quality needs its own labelled evaluation:

- canonical drug/manufacturer merging;
- SentenceTransformer or pgvector matching;
- custom NER, Neo4j, Elasticsearch or LLM extraction;
- authentication, chatbot and mobile application.

The live UI therefore labels drug and manufacturer pages as exact source mentions, not canonical entities.

## Evidence and commands

See:

- `docs/data-audit.md`
- `docs/extraction-benchmark.md`
- `docs/row-extraction-evaluation.md`
- `docs/current-nsq-source-audit.md`
- `data/samples/ground_truth/regulatory_rows.jsonl`

Run the reproducible workflow from the repository root:

```powershell
backend\.venv\Scripts\python.exe scripts\benchmark_extraction.py
backend\.venv\Scripts\python.exe scripts\extract_regulatory_rows.py
backend\.venv\Scripts\python.exe scripts\build_ground_truth.py
backend\.venv\Scripts\python.exe scripts\evaluate_row_extraction.py
backend\.venv\Scripts\python.exe scripts\load_database.py
backend\.venv\Scripts\python.exe scripts\ingest_current_nsq.py
backend\.venv\Scripts\python.exe -m pytest -q
```

Do not perform entity resolution on regulatory rows whose extraction quality has not first been measured and validated.
