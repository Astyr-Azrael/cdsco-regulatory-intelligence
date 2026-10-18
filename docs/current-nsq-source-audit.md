# Current CDSCO NSQ Source Audit

## Audit Scope

- Page: `https://cdscoonline.gov.in/CDSCO/viewPublicNSQDrug`
- Observed on: 2 October 2026 (Asia/Calcutta)
- Method: normal browser load, DOM/control inspection, public page JavaScript inspection and a read-only request to an endpoint explicitly referenced by that JavaScript
- Authentication/CAPTCHA: none encountered for the tested page and public NSQ data request

This is a point-in-time technical audit, not a claim that the portal contract is permanent.

## Static and Dynamic Behaviour

The page is a server-rendered shell containing NSQ and Spurious tabs, filters and empty DataTables targets. On page ready, JavaScript performs same-origin AJAX requests, parses the returned JSON string and supplies `aaData` to client-side DataTables. Search, sort and the visible 10/25/50/100-page-size controls operate on the records already returned to the browser.

At audit time, the default NSQ table displayed `Showing 1 to 10 of 220 entries` and the latest visible reporting month was `AUG-2026`.

## Filters

The NSQ tab exposed:

- year: 2019 through 2026;
- month: dynamically loaded after selecting a year;
- reporting source: `All`, `State` or `CDL` (displayed as CDSCO Labs).

The filter is applied only after both reporting month and reporting source are selected.

## Observed Public Requests

These paths are taken from the page's own active JavaScript; none were invented.

| Method | Path | Parameters | Purpose |
|---|---|---|---|
| GET | `/CDSCO/reportingYears` | `tab=nsq` or `tab=spurious` | Populate years |
| GET | `/CDSCO/publicReportingMonths` | `year`, `tab` | Populate reporting months |
| GET | `/CDSCO/publicNsqDrugTable` | none | Load the current/unfiltered NSQ dataset |
| GET | `/CDSCO/filteredNsqDrugTable` | `month`, `source`, `tab` | Load filtered NSQ records |
| GET | `/CDSCO/viewPublicSpuriousDrugData` | none | Load the current/unfiltered spurious dataset |
| GET | `/CDSCO/filteredSpuriousDrugTable` | `month`, `source`, `tab` | Load filtered spurious records |
| GET | `/CDSCO/statesPendingSubmission` | optional `month` | List states pending submission |

## Response Format

`/CDSCO/publicNsqDrugTable` returned an object with:

```json
{
  "iTotalDisplayRecords": 220,
  "iTotalRecords": 220,
  "aaData": []
}
```

Each observed NSQ member contained:

```text
str_product_name
str_batch_no
dt_manufacturing_date
dt_expiry_date
str_manufactured_by
str_nsq_result
str_reporting_source
str_reported_by_lab_or_state
dt_reporting_month_year
```

The spurious JavaScript expects:

```text
product_name_from_dtl
str_batch_no
dt_manufacturing_date
dt_expiry_date
str_spurious_manufacturer_name
str_spurious_manufactured_by
str_reporting_source
str_reported_by_lab_or_state
dt_reporting_month_year
str_nsq_remarks
str_firm_reply
```

The browser code treats the response as text and calls `JSON.parse`, so an ingester should accept either an already-decoded JSON object or a JSON-encoded response body after validating the content type/body.

## Pagination

The public NSQ endpoint returned all 220 records in a single response during this audit. Pagination was performed by DataTables in the browser, not through observed server-side `start`, `length`, cursor or page parameters. An ingester should not assume this will remain true; it should compare `aaData.length`, `iTotalRecords` and `iTotalDisplayRecords` on every run.

## Record Identifiers and Dates

No stable record identifier was exposed in the observed NSQ payload. The visible serial number is generated from the DataTables row position and is not a source identifier. Therefore:

- retain a hash of the complete raw source record;
- build a provisional natural key from source system, reporting month, product, batch, manufacturer, reporting source and reporting laboratory/state;
- retain the raw record so key changes can be audited;
- do not present the generated table position as an official CDSCO ID.

Manufacturing date, expiry date and reporting month/year are strings such as `Jun-2026`, `Dec-2026` and `AUG-2026`. Preserve them verbatim and normalize separately.

## Access Restrictions

The tested read-only page and NSQ data endpoint were publicly accessible without login or CAPTCHA. The page disables right-click and common developer-tool keyboard shortcuts in client JavaScript; that is a presentation control, not an authorization mechanism. This audit did not bypass authentication, CAPTCHA, rate limits or any browser security warning. No bulk or repeated collection was performed.

## Recommended Ingestion Method

1. Use ordinary HTTPS GET requests only to the observed same-origin public endpoints.
2. Fetch filter metadata, then request one bounded reporting month/source at a time when historical backfill is needed.
3. Apply a descriptive user agent, conservative rate limits, retries with backoff and a stop-on-schema-change policy.
4. Save the raw response unchanged with URL, parameters, retrieval timestamp, status, media type and SHA-256 hash.
5. Validate count fields and required keys before accepting rows.
6. Standardize portal fields into the same raw parsed-record schema used for legacy PDFs, using an official source URL plus record hash in place of PDF page coordinates.
7. Keep portal records and PDF-extracted records distinguishable through `source_system` and provenance fields; deduplicate only after evidence-preserving persistence exists.
8. Treat the absence of a stable public ID as a known limitation, not as permission to invent one.

The current portal is technically suitable for a cautious structured ingestion adapter. Production collection should still verify site terms, monitor schema changes and avoid aggressive polling.
