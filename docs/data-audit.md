# CDSCO Data Audit

Audit run: 2026-09-30T19:31:20Z
Phase: real source-ingestion prototype
Scope: five official public documents; no row-level regulatory-field parsing

## Sources Tested

### Legacy CDSCO Alerts archive

- Source: `https://www.cdsco.gov.in/opencms/opencms/en/Notifications/Alerts/`
- Access result: HTTP 200; no authentication or CAPTCHA observed.
- Representation: server-rendered HTML containing one alert table.
- JavaScript requirement: none for the table metadata used by this pipeline.
- Pagination observed: none; 300 numbered rows were present in the retrieved HTML.
- Index fields observed: title, release date, download link and displayed PDF size.
- Document-link behavior: each table link returns a short HTML page containing a same-host iframe. The iframe points to the original PDF under the official CDSCO resources path.
- Automation decision: suitable for the bounded Phase 1 audit with conservative access and local raw-file caching.

### Current public NSQ interface

- Source: `https://cdscoonline.gov.in/CDSCO/viewPublicNSQDrug`
- The public page exposes year, month and reporting-source filters.
- Its record retrieval behavior was not used in this phase because the static page response does not expose the result rows needed for the reproducible index parser.
- No attempt was made to bypass client-side behavior or access controls.

## Source Collection Method

1. Request the official legacy index using an identifiable academic-research user agent.
2. Preserve the response bytes unchanged under `data/raw/html/`.
3. Calculate a SHA-256 hash for the index snapshot.
4. Parse only numbered table rows.
5. Derive alert categories only from explicit title terms such as `NSQ`, `State NSQ`, `Spurious` or `Revised drug alert`.
6. Request the official document-link wrapper.
7. Follow only the wrapper's same-host iframe source.
8. Validate the `%PDF` file signature before storage.
9. Store the original bytes under `data/raw/pdf/` using a deterministic hash-bearing filename.
10. Extract page-separated text with PyMuPDF and write evidence-oriented JSONL.

The saved index snapshot hash was:

```text
cb97b574585f7ac39c34932fa0a1bb7d5cd9af8aa8868e818a3d116829d6a9cf
```

## Sample Documents

| Official alert title | Type | Release date | Pages | Bytes | SHA-256 |
|---|---|---:|---:|---:|---|
| CDSCO NSQ ALERT FOR THE MONTH OF June 2025 | NSQ | 2025-07-18 | 6 | 188,795 | `e4d55f085dcfb29bb808c55ddd89a374c1f256c4a620af95a2c50144ce410509` |
| STATE NSQ ALERT FOR THE MONTH OF June 2025 | STATE_NSQ | 2025-07-18 | 15 | 424,014 | `43de100540526f71bd7555afeecb84ffc64c308e1a564d37c91e0446c2b307c3` |
| List of spurious Drugs for the month of June-2025 | SPURIOUS | 2025-07-18 | 2 | 129,866 | `7ddd0c43d13b56f76ed1a4097c992a963e71f45430c52f25429d389c28c85e0b` |
| Revise list drug alert May-2025 | REVISED_ALERT | 2025-07-18 | 1 | 170,579 | `0ba4117374cfb2bb778fdc80191c2c352dcc3eb755734adff3437de232d60ff0` |
| List of Drugs, Medical Devices, Vaccine and Cosmetics declared as Spurious for the Month of May-2025 | SPURIOUS | 2025-06-20 | 2 | 204,765 | `8b0877f57cee6fd2e9ea7174be7124250dd565daaccb03d6116fc9c4d7aea15b` |

All five documents were downloaded from official CDSCO hosts. Their wrapper and resolved PDF URLs are retained in `data/interim/cdsco_phase1_audit.json`.

## Alert / Index Structure

The archive uses five visible columns:

```text
serial number | title | release date | download link | displayed PDF size
```

Dates use forms such as `2025-Jul-18` and normalize cleanly to ISO dates. Titles vary in spelling and capitalization. The alert's release date is not the same as the month described inside the alert and is stored separately.

The archive also contains notices and unrelated documents. A title containing the letters `NSQ` is not sufficient by itself: the “Availability of Not Standard Quality (NSQ) Alert on New Link” notice was deliberately excluded from the regulatory sample.

## PDF Format Observations

- All five PDFs are machine-readable; no OCR was required.
- The CDSCO NSQ and State NSQ documents use multi-page tables with recurring concepts such as product name, batch, manufacturing date, expiry date, manufacturer, result and reporting laboratory.
- The State NSQ sample is materially longer than the central-laboratory sample: 15 pages versus 6 pages.
- Spurious-document tables add columns such as drawn-by authority, firm reply and remarks.
- Text extraction retains content but does not reconstruct a reliable row grid.
- Long product names, manufacturer addresses, reasons and remarks wrap across several visual lines.
- Column headings may be split in extracted text, for example `Manufact / uring / Date`.
- Reading order can place content from distant columns next to one another.
- No sample page was empty after PyMuPDF extraction.

## Fields Consistently Available

At index level, all five selected records provided:

- official alert title,
- release date,
- official wrapper URL,
- resolved official PDF URL,
- displayed size text,
- retrieval timestamp.

At document level, the five samples provided machine-readable text, page count, byte size and file hash. Product, batch, manufacturer and date-related headings were present, although this phase does not claim reliable row-level parsing.

## Fields Inconsistently Available

- Reporting-laboratory terminology differs between central and State NSQ documents.
- Spurious documents use `Reason for failure`, `Drawn By`, `Firm's reply` and `Remarks`, rather than the central NSQ table shape.
- Some titles describe a month different from the release date.
- The archive title `Revise list drug alert May-2025` resolves to a PDF whose visible internal heading refers to a revised January 2025 list. Both values are preserved; the pipeline does not silently reconcile the discrepancy.
- Exact row boundaries, manufacturer addresses and long failure reasons are not consistently recoverable from plain text alone.

## Successful Extraction Cases

- 300 archive rows discovered from one preserved HTML response.
- Five of five representative documents downloaded successfully after resolving the official same-host iframe wrapper.
- Five of five PDF signatures validated.
- Five of five SHA-256 hashes generated.
- Five of five documents produced page-separated PyMuPDF text.
- Zero empty-text pages across the representative set.
- A second complete run recognized all five PDFs as duplicates and created no additional raw PDF files.
- Five intermediate JSONL records were produced with unparsed regulatory fields retained as `null`.

## Failed / Difficult Extraction Cases

The first download attempt correctly rejected the CDSCO wrapper responses because they were HTML rather than PDF files. Inspection showed that each wrapper contains a same-host iframe pointing to the official PDF. The downloader was updated to resolve exactly that documented pattern and continues to reject other HTML/non-PDF responses.

No final document downloads failed. The difficult remaining problem is table reconstruction: PyMuPDF provides useful text, but visual table rows can be broken, interleaved or continued across pages. No row-level values are reported as parsed in Phase 1.

## Document Variations

- Central laboratory NSQ table: 6 pages.
- State laboratory NSQ table: 15 pages and different reporting-laboratory wording.
- Spurious lists: 2 pages with additional investigative and remarks columns.
- Revised list: 1 page, with a source-title/document-heading discrepancy.
- Wrapped product names and manufacturer addresses occur throughout the sample.
- Page length, number of columns and column widths differ by regulatory category.

## Recommended Parser Strategy

1. Keep PyMuPDF as the primary page-text and provenance extraction engine.
2. Preserve current raw text and page boundaries unchanged.
3. Evaluate pdfplumber on these exact five files for words-with-coordinates and table reconstruction.
4. Implement category-specific row parsers rather than one universal table rule.
5. Validate reconstructed rows against page images and a manually labelled mini dataset.
6. Keep uncertain fields as `null` and attach page/row evidence to accepted values.
7. Do not begin entity resolution until row-level extraction precision is measured.

## Technical Limitations

- The legacy archive may no longer be the long-term publication interface for new NSQ data.
- The current public NSQ interface still requires a separate network/API behavior audit.
- HTML structure and wrapper behavior can change without notice.
- Raw and interim data are Git-ignored and must be regenerated with the documented command.
- PostgreSQL is not connected and the API does not yet expose the intermediate records.
- This audit demonstrates document-level ingestion, not complete historical coverage or reliable row-level extraction.

## Phase 2 Recommendations

- Benchmark PyMuPDF word coordinates against pdfplumber table extraction on the five preserved PDFs.
- Create manually verified row fixtures for central NSQ, State NSQ, spurious and revised layouts.
- Add row-level extraction with source page, bounding box or line evidence.
- Separate source release date, document-covered month and any event/manufacturing/expiry dates.
- Add `source_documents` and `ingestion_runs` persistence only after the intermediate schema is stable.
- Connect FastAPI and the frontend only after the parsed records pass extraction-quality checks.
