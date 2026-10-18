# Final presentation outline

Working assumption: 12 slides for a 10-12 minute academic presentation. Adjust when the college time limit is confirmed.

## 1. Title

Entity-Centric Drug Regulatory Intelligence from Fragmented CDSCO Alerts

Subtitle: Provenance-preserving extraction, entity resolution and longitudinal regulatory histories

## 2. Problem and research gap

- CDSCO records are split across heterogeneous PDFs and a current portal.
- Row structure, naming and source evidence vary.
- Document search cannot reliably reveal repeated entities.
- Aggressive fuzzy matching can create false regulatory relationships.

Visual: fragmented sources converging into a traceable entity history.

## 3. Authoritative sources and bounded scope

- Eight legacy PDFs from 1 January-31 December 2025.
- Central NSQ, State NSQ, Spurious and Revised Alert.
- One August 2026 public NSQ portal snapshot.
- 599 records across nine official sources.

Visual: source timeline with explicit “indexed corpus” label.

## 4. System architecture

Show the architecture diagram from `docs/architecture/final-architecture.md`: acquisition, preservation, extraction, evaluation, entity resolution, database, API and React.

## 5. Layout-aware extraction

- PyMuPDF text and coordinate evidence.
- `pdfplumber` table geometry.
- Category-specific parsers.
- Raw cells, page, row, bounding box and SHA-256 retained.

Visual: rendered PDF row beside its structured representation.

## 6. Extraction evaluation

Editable table:

| Measure | Result |
|---|---:|
| Expanded legacy rows | 379 |
| Unseen labelled rows | 11 |
| Rows reconstructed | 11/11 |
| Manufacturer normalized accuracy | 81.8% |
| Other labelled fields normalized accuracy | 100% |

Callout: State NSQ manufacturer punctuation/address reconstruction is the main observed error.

## 7. Entity-resolution methodology

Normalization, candidate blocking, RapidFuzz features, context compatibility, thresholds and review queue. State explicitly that normalized clusters form automatically, while accepted versioned source reviews add explicit links. Unreviewed suggestions remain separate.

## 8. Entity-resolution results

Editable table:

| Metric | Manufacturer | Drug/product |
|---|---:|---:|
| Proposal precision | 1.000 | 1.000 |
| Proposal recall | 0.900 | 0.500 |
| Proposal F1 | 0.947 | 0.667 |

Final counts: 399 organization clusters, 505 product clusters, 17 primary source decisions and 348 unresolved suggestions. Metrics use the 40-pair source-backed candidate sample, excluding three ambiguous product pairs. Applied review results are regression only; disclose small primary annotations and limited held-out product recall. The original 16-pair perfect fixture is tuned regression evidence.

## 9. Entity-centric regulatory histories

Show one canonical profile structure: aliases, match evidence, linked products/batches, chronological events and official source links. Explain how entity search reveals records that exact source-mention search separates.

## 10. Application demonstration

Sequence: Search, canonical entity profile, event detail, provenance panel, official PDF. Include Overview, Sources and Analytics as secondary screens.

## 11. Validation, ethics and limitations

- 33 automated tests pass; one live test is opt-in.
- SQLite migration and frontend production build verified.
- Indexed-corpus analytics are not safety or prevalence scores.
- Small evaluation sets need second human review.
- PostgreSQL/HTTPS require final deployment validation.

## 12. Conclusion and future work

Core result: fragmented records become searchable longitudinal histories without losing the official evidence chain.

Next: expand blind annotations, complete second review, adjudicate fuzzy candidates, validate scheduled PostgreSQL ingestion and investigate evidence-supported revision links.
