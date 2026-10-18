# CDSCO PDF Extraction Benchmark

## Expanded bounded-corpus run (October 2026)

The benchmark now covers eight preserved PDFs rather than requiring exactly five. The added documents are May 2025 central NSQ, May 2025 State NSQ and April 2025 spurious publications. Visual inspection confirmed the supported eight-column central/state family and supported spurious table family. The machine-readable benchmark was regenerated at `data/interim/extraction_benchmark.json`.

## Scope

This benchmark compares four extraction paths on eight official CDSCO PDFs: the five Phase 1 documents plus three held-out May/April 2025 documents acquired during corpus expansion. Measurements were produced locally by `scripts/benchmark_extraction.py`; they are not estimates. The documents contain 379 regulatory rows in total: 113 central NSQ, 258 state NSQ, 7 spurious and 1 revised-alert row.

## Documents Tested

| Document | Type | Pages | Verified regulatory rows |
|---|---|---:|---:|
| CDSCO NSQ Alert for June 2025 | Central NSQ | 6 | 55 |
| State NSQ Alert for June 2025 | State NSQ | 15 | 130 |
| Spurious list dated 20 June 2025 | Spurious | 2 | 2 |
| Spurious Drugs for June 2025 | Spurious | 2 | 4 |
| Revised Drug Alert for May 2025 | Revised | 1 | 1 |
| CDSCO NSQ Alert for May 2025 | Central NSQ | 7 | 58 |
| State NSQ Alert for May 2025 | State NSQ | 19 | 128 |
| Spurious list dated 20 May 2025 | Spurious | 1 | 1 |

All pages were rendered to PNG and visually inspected. No OCR was required.

## Methods Compared

| Document type | PyMuPDF text | PyMuPDF coordinates | pdfplumber words | pdfplumber tables | Recommended |
|---|---:|---:|---:|---:|---|
| CDSCO NSQ | 148.8 ms | 30.7 ms | 1,536.5 ms | 1,524.5 ms | pdfplumber tables for rows; PyMuPDF coordinates for preserved word evidence |
| State NSQ | 453.9 ms | 87.4 ms | 5,096.1 ms | 7,280.1 ms | pdfplumber tables for rows; PyMuPDF coordinates for preserved word evidence |
| Spurious | 33.2 ms | 10.4 ms | 195.0 ms | 206.2 ms | pdfplumber tables with category-specific continuation-row repair |
| Revised | 29.1 ms | 16.4 ms | 139.9 ms | 178.3 ms | pdfplumber tables with the revised-alert parser |

Times are single local runs and are useful for relative comparison, not as a production throughput guarantee.

## Central NSQ Results

Both central alerts use consistent eight-column ruled tables. Plain text preserved content but flattened column relationships, while both coordinate-word methods retained positions. The category parser reconstructed 55 June rows and 58 held-out May rows. Wrapped product, manufacturer and failure-reason cells remained associated with their numbered rows.

## State NSQ Results

Both state alerts use an eight-column layout, with dense multiline cells and greater formatting variation. The state parser reconstructed 130 June rows and 128 held-out May rows. Nineteen records across the expanded legacy corpus are `PARTIAL` because at least one date could not be normalized conservatively. Those strings are retained verbatim rather than silently corrected.

## Spurious Results

The tested spurious publications use ten-column tables, with one June extraction presenting twelve columns on its first page because product names spill into continuation rows. A spurious-specific repair joins only unnumbered continuation rows to the adjacent numbered record and expands the provenance bounding box. Seven regulatory rows were reconstructed across the three files.

## Revised Alert Results

The revised-alert PDF contains one numbered correction row in a ten-column table. The parser retains its source serial (`19`), category-specific authority field, page and row bounding box. It is not treated as a replacement for the original alert at this phase.

## Row Reconstruction Accuracy

The parsers produced 379 rows: 360 `PARSED`, 19 `PARTIAL`, 0 `REQUIRES_REVIEW` and 0 `FAILED`. The original 77-row regression subset was checked against rendered pages. A separate 11-row set was manually transcribed from the three newly acquired documents before parser execution and measures held-out-document behavior. See `docs/row-extraction-evaluation.md` for field-level results and validation limitations.

## Multi-line Cell Handling

Ruled-table extraction preserves multiline text within a cell. The parsers normalize whitespace only, preserve the raw extracted cells, and retain a pipe-delimited reconstructed row. The spurious parser additionally handles visually continued product names whose PDF geometry produces unnumbered table rows.

## Page-Break Handling

Repeated page headers are rejected unless the first cell contains a valid serial number. The source serial is used as `source_row`; `source_page` and the table-row bounding box identify the supporting location on the PDF page. No cross-page row merge was required in this sample.

## Performance

PyMuPDF coordinate extraction was the fastest structured method on every file. `pdfplumber` table extraction was slower but supplied the strongest row/column reconstruction. The chosen hybrid deliberately favors extraction quality over raw speed while retaining PyMuPDF coordinate extraction as a reusable evidence path.

## Failure Modes

- Plain text loses table boundaries and is unsuitable as the primary row parser.
- Word coordinates alone require document-specific column thresholds.
- Repeated headers and continuation rows inflate raw table row counts.
- Visually spaced text such as `F e b - 2 5`, malformed values such as `Apr--2026`, and full dates such as `12-09-2024` cannot be safely normalized by the conservative month-year parser.
- Page geometry and column counts vary by regulatory category, so a universal parser would obscure real differences.

## Recommendation

Use category-specific parsers over `pdfplumber` table geometry for the tested document families. Preserve PyMuPDF words and their coordinates as independent page evidence. Keep raw cells and raw date strings, apply only conservative normalization, and route unsupported layouts to review rather than coercing them into a schema.
