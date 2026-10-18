# CDSCO Regulatory Intelligence Implementation and Method Selection

Entity Centric Drug Regulatory Intelligence from Fragmented CDSCO Alerts

B Tech Honours Data Engineering Mini Project

Final local demonstration release 19 October 2026

## Project achievement and release scope

We built a working pipeline that converts selected official CDSCO PDFs and a public portal snapshot into source-traceable regulatory records and organization/product histories. The final demonstration supports source acquisition, layout-aware extraction, validation, structured storage, normalization, similarity proposals, recorded source reviews, search and analytics through a web application.

The release is a bounded local academic implementation. It supports a defensible demonstration of the engineering workflow and selected reviewed entity links. It does not establish complete CDSCO coverage, universal parser accuracy or comprehensive real-world identity resolution.

| Verified result | Value |
|---|---:|
| Official regulatory source rows | 599 |
| Preserved source documents and snapshots | 9 |
| Legacy PDF rows and portal rows | 379 and 220 |
| Organization and product clusters | 399 and 505 |
| Primary source review decisions | 17 |
| Remaining unreviewed fuzzy suggestions | 348 |
| Automated tests in the final environment | 33 passed and 1 optional live test skipped |

This report explains what we implemented, why each component was selected, the alternatives we considered, and the evidence supporting the final claims. Our main contribution is the integration of provenance, extraction and conservative entity linking. React is the presentation layer rather than the central technical contribution.

<!-- page -->

# 1 The problem and our objectives

CDSCO information is fragmented across central NSQ alerts, State NSQ alerts, spurious-drug publications, revised alerts and a separate public portal. A publication is easy to retrieve as a document, but a reader must manually connect product wording, manufacturers, batches and dates across documents. Name variants, combined name/address cells and heterogeneous table layouts make that reconstruction difficult.

We aimed to collect authoritative public material, retain the original bytes, reconstruct rows, normalize source mentions and connect supported aliases to organization and product clusters. The user should be able to search a name, view related records over time and open the official source supporting each finding.

## What a successful demonstration proves

The demonstration proves that one preserved official row can be followed through extraction, storage and entity linkage into a visible regulatory history. It also proves that source hashes, page/row evidence and original wording survive the transformation. Repeated ingestion should converge on the same records.

We distinguish a regulatory source row from an independently deduplicated real-world event. A changed portal snapshot may repeat an earlier event, so counting snapshots without event deduplication can overcount real-world activity. The frozen dataset contains a single portal snapshot.

## Scope and interpretation

The eight PDF publications contain 379 rows from the tested April to June 2025 alert periods. The public portal snapshot contributes 220 August 2026 rows. These sources demonstrate heterogeneous ingestion and cross-source histories, but leave substantial gaps in the archive.

NSQ means Not of Standard Quality. Our system reproduces regulator-published findings and organizes evidence. It does not predict medicine safety, rank manufacturers by risk or infer that every batch of a product shares the cited finding.

<!-- page -->

# 2 System architecture and data flow

We use a layered design so that changing a parser or match decision does not destroy the underlying evidence. The raw layer holds original HTML, PDF and JSON files. The parsed layer stores reconstructed regulatory rows. The entity layer stores normalized clusters, aliases and reviewed relationships. FastAPI queries those layers and React displays their results.

| Layer | Responsibility | Main implementation |
|---|---|---|
| Acquisition | Public index parsing and bounded source collection | scraper sources and download modules |
| Extraction | PDF page evidence and ruled-table reconstruction | extraction and category parser modules |
| Validation | Required fields, date normalization and status | parser common utilities and portal adapter |
| Persistence | Source metadata, rows and process logs | SQLAlchemy models and loaders |
| Entity linking | Comparison keys, candidates, scores and decisions | normalization and entity resolution modules |
| Retrieval | Records, profiles, histories and analytics | FastAPI routes |
| Presentation | Search, source evidence and contextual histories | React pages |

The data model separates source_documents, ingestion_runs and parsed_regulatory_records from canonical_manufacturers, manufacturer_aliases, canonical_drugs and drug_aliases. An alias links a cluster directly to an original regulatory row. That row links to the official source and its hash.

entity_matches records comparison keys, scores, decisions and evidence JSON. Its references to entities are logical rather than database foreign keys. web_usage_events is a separate application instrumentation table. It does not contribute to regulatory statistics.

We selected a relational model because the main questions involve explicit relationships and filters: which rows mention this entity, which document supports this row, and which dates and batches occur in those records. These joins are manageable without a graph database for this project size.

<!-- page -->

# 3 Official acquisition and provenance

The legacy adapter reads the public alerts table and extracts title, release date, category, download URL and displayed size. The preserved index has 300 numbered rows; this does not mean all 300 publications were ingested. We selected eight publications within explicit date and category limits.

Some official download links return an HTML wrapper containing the actual PDF in an iframe. The downloader follows only the observed same-host pattern, validates the PDF signature and calculates SHA-256 while preserving the returned bytes. It rejects an unrelated HTML body rather than saving it as a PDF.

The current portal uses a separate structured adapter. It validates the aaData collection, declared row count and required keys before converting each row into the common schema. The original JSON remains available. Portal row position is local snapshot provenance because the observed response lacks stable official row identifiers.

## Evidence retained for each record

A legacy row retains its source hash, filename, page, visible serial, bounding box, reconstructed raw cells, row text, parser name, parser version and validation warnings. Portal records retain the official page, snapshot hash, raw JSON row and response position.

All nine database source hashes were compared with the actual preserved files and matched. The release verification script repeats this check. Hash equality proves consistency with the preserved snapshot; it does not certify the regulator's underlying claims or guarantee that the official live URL still serves identical bytes.

## Duplicate handling and snapshot history

Source content hashes are unique in the database. Legacy source rows are keyed by document and serial for the tested layouts. An unchanged portal response does not create another source row set. Repeated retrieval may preserve another raw file with the same hash because filenames include retrieval time; that does not duplicate database records.

An offline restore command now loads the frozen portal response without making a network request. This makes the classroom demonstration reproducible even if the public source changes or is temporarily unavailable.

<!-- page -->

# 4 PDF extraction and the measured comparison

We compared PyMuPDF plain text, PyMuPDF words with coordinates, pdfplumber words and pdfplumber tables on the same preserved PDFs. The task required cell and row reconstruction, so extraction speed alone could not determine the choice.

| Document category | PyMuPDF text ms | PyMuPDF coordinates ms | pdfplumber words ms | pdfplumber tables ms |
|---|---:|---:|---:|---:|
| Central NSQ | 148.8 | 30.7 | 1536.5 | 1524.5 |
| State NSQ | 453.9 | 87.4 | 5096.1 | 7280.1 |
| Spurious | 33.2 | 10.4 | 195.0 | 206.2 |
| Revised Alert | 29.1 | 16.4 | 139.9 | 178.3 |

These are category means from one local eight-document benchmark run, rather than production throughput guarantees. Central and State each contain two files, Spurious contains three, and Revised Alert contains one.

PyMuPDF coordinates were useful for fast page evidence. pdfplumber table geometry supplied the strongest usable row and column structure on the tested ruled layouts. We therefore retained both: PyMuPDF for text/coordinate evidence and pdfplumber for category-specific row reconstruction. The plain-text output flattened column relationships and was unsuitable as the main row parser.

Central and State NSQ use the tested eight-column family. Spurious publications require ten/twelve-column mapping and continuation-row repair. The revised parser reuses the compatible spurious layout through its own category route. Shared logic reflects verified common layouts rather than claiming every category has an independent algorithm.

The eight PDFs reproduce 379 rows exactly: 360 PARSED and 19 PARTIAL. The partial rows retain useful evidence while recording conservative date-normalization failures. No OCR was needed for these machine-readable files. OCR remains an option for a future scanned layout; we did not benchmark it or claim it would be less accurate.

<!-- page -->

# 5 Normalization and entity meaning

Manufacturer normalization applies Unicode cleanup, case folding, punctuation and whitespace normalization, and common corporate abbreviations such as Pvt and Ltd. A splitter identifies apparent embedded address boundaries. Addresses are retained separately and common location terms are normalized for comparison.

A manufacturer cluster represents an organization name. It is not a verified legal registry identity or a single factory. A company can have records from different sites, so profiles retain every observed address and the report never treats those addresses as one manufacturing unit. Source-specific unit wording remains relevant evidence.

Twelve values such as Under Investigation or Not Mentioned are preserved as raw manufacturer text but excluded from identity clusters. Treating every occurrence of Under Investigation as one manufacturer would create a false history.

Product normalization retains ingredient wording, strength, dosage form, explicit numbers, decimal points and concentration denominators. Drug 2.5mg must remain different from Drug 25mg, and 1mg/5ml must remain different from a string listing 1mg and 5ml separately. Pharmacopoeia conflicts and differing numeric formulation wording block product match proposals.

## Why equality alone is insufficient

Normalized equality removes superficial variation, but an omitted corporate suffix or a broken word can still produce separate keys. In the original corpus, Martin and Brown appeared in two clusters despite the same distinctive name and matching Baddi address. A recorded source review now links those variants into one 20-record history.

Conversely, products containing different strengths or dosage forms must remain separate even when a fuzzy score is high. A generic name without a stated strength cannot always be linked confidently to a fully specified formulation. We preserve that uncertainty.

Normalized equality receives a score of 100 on the comparison scale. This is not 100 percent identity confidence. The UI identifies equality-only clusters and primary reviewed links separately.

<!-- page -->

# 6 The selected matching method

We selected a transparent matching pipeline: normalized comparison keys, blocked candidate generation, RapidFuzz similarity features, explicit compatibility rules and a recorded source-review stage. No neural model is trained in the final implementation.

Candidate blocks use distinctive name tokens, name prefixes and location terms. Large blocks above 80 members are skipped because common terms can create low-value Cartesian comparisons. Blocking reduces comparisons, but omitted candidates remain a recall risk.

RapidFuzz provides character and token similarity functions [1]. We retain ratio, WRatio, token sort ratio and token set ratio. The aggregate uses weights 0.45 for WRatio, 0.35 for token set ratio and 0.20 for ratio. These weights and the thresholds are engineering heuristics, not calibrated probabilities.

Manufacturer proposals use match/review thresholds of 96 and 86 with address context. Product proposals use 98 and 90 with numeric, strength, form and standard checks. A score above the match threshold still requires an explicit source decision before it changes deployed clusters.

| Method | Role in our implementation | Decision |
|---|---|---|
| Raw exact equality | Minimal comparison baseline | Too sensitive to formatting variants |
| Normalized equality | Initial deterministic clusters | Retained with equality-only status |
| RapidFuzz with context | Interpretable candidate proposals | Selected baseline |
| TF IDF or supervised classifier | Potential learned matching alternative | Not benchmarked; labelled data is small |
| SentenceTransformer embeddings | Potential semantic similarity | Not retained without measured benefit |
| spaCy custom NER | Potential entity span extraction | Not trained; structured fields already available |
| LLM extraction or matching | Potential document adaptation | Not benchmarked; unsupported outputs complicate provenance |

SentenceTransformer similarity models compare sentence embeddings [4]; spaCy training requires suitable annotated training data [5]. Neither capability by itself establishes legal company identity or exact formulation equivalence. We did not run a head-to-head neural benchmark, so this table explains design suitability rather than claiming model superiority.

<!-- page -->

# 7 Source review and entity evaluation

Seventeen versioned decisions now operate on actual source mentions: eleven accepted links and six rejections. Each decision includes both immutable source hashes, source serials, raw mentions, a rationale and reviewer attribution. Rebuilding the entity layer reapplies accepted links and retains rejections. Fuzzy proposals without a decision remain unresolved.

These decisions are a primary assistant review of source text. We do not claim independent human annotation or a legal identity investigation. The source evidence makes each decision inspectable by the mentor.

The original 16 pairs remain a tuned regression fixture. Forty additional corpus pairs contain 20 MATCH, 17 NO_MATCH and three AMBIGUOUS labels. Ambiguous rows are excluded from binary metrics. The labels follow our stated organization/product linking policy and come from a candidate-enriched sample. They do not estimate population accuracy.

| Method and sample | Precision | Recall | F1 |
|---|---:|---:|---:|
| RapidFuzz proposal manufacturers 20 pairs | 1.000 | 0.900 | 0.947 |
| RapidFuzz proposal products 17 binary pairs | 1.000 | 0.500 | 0.667 |
| Deployed reviewed clusters manufacturers 20 pairs | 1.000 | 0.700 | 0.824 |
| Deployed reviewed clusters products 17 binary pairs | 1.000 | 0.400 | 0.571 |

The deployed-cluster rows include applied decisions and therefore are regression measurements. Twenty-three annotations were held out from review application. The held-out proposal F1 is 1.000 on eleven manufacturer pairs and 0.286 on nine binary product pairs. The latter has recall 0.167. This reveals the limitations of a strict product threshold.

Held-out fuzzy positives remain outside deployed clusters by policy, so deployed held-out positive recall is zero on this difficult sample. We report this openly. Candidate generation covers all twenty annotated positives, but the pairs were selected from candidates; this is conditional coverage, not independent global blocking recall.

<!-- page -->

# 8 Extraction evaluation and validation

We maintain two extraction datasets. The original 77-row set was seeded from parser output and then checked visually. It is a regression fixture. The later eleven rows were transcribed from three additional PDFs before parser execution, making them more useful for testing unseen documents. They still have only primary review.

All eleven unseen rows are reconstructed. Product, batch, dates, finding, laboratory and available authority have 100 percent normalized equality in this small set. Product exact equality is 54.5 percent because punctuation and whitespace differ. Manufacturer normalized equality is nine of eleven, or 81.8 percent, with the two disagreements concentrated in State NSQ manufacturer/address reconstruction.

## Corrected metric definition

A wrong nonempty field prediction introduces a false positive and misses the expected value, so it must also count as a false negative. The earlier implementation counted only the former and could report perfect recall even with incorrect values. This has been corrected and the reports regenerated.

For the eleven-row manufacturer field, corrected precision, recall and F1 are each 0.818. State NSQ manufacturer normalized equality is 0.600 on five examples. These are field-value equality metrics on labelled rows; they do not measure unlabelled false rows, all-table detection accuracy or complete archive recall.

## Quality statuses

PARSED means the required extracted fields are present and the implemented normalization checks did not raise a warning. PARTIAL means useful source-backed content exists but something such as a date remains incomplete. These states describe extraction quality, not regulatory severity.

Unexpected PDF layouts remain a limitation. Current parsers skip unrecognized column structures, so a new template can produce missing rows. The frozen release is validated on its eight preserved PDFs. Extending coverage should involve a new source sample, independent labels, layout inspection and regression tests rather than weakening validation.

<!-- page -->

# 9 Search histories and the user interface

The React application exposes overview, search, regulatory records, entity profiles, contextual batch occurrences, event detail, timeline, analytics and sources. FastAPI supplies real database values. Loading, empty and error states are visible, and a failed API request does not substitute the old six-record fixture.

Entity search matches canonical names and retained source mentions. A profile shows aliases, observed addresses or strength/form signals, primary review rationale and linked records. Histories sort by publication/reporting date, source, serial and record ID. All 904 final organization/product histories pass the chronological check.

The portal reports a month rather than a verified day. We keep month-start internally for sorting and display the reporting month in the UI. PDF dates remain release dates. A timeline therefore represents publication/reporting chronology rather than the exact laboratory test date.

## Batch identity correction

TST2301 occurs in five different product records. The original batch page selected the first row, which could imply a single batch identity. The final endpoint groups all occurrences by product, manufacturer and observed site address, and the page shows all five contexts with their own records and histories.

This grouping avoids assuming that a batch number is globally unique. It may split equivalent address variants because we prioritize retaining uncertainty over collapsing sites without evidence.

## Two analytics purposes

Regulatory analytics summarize source coverage, event categories, parse statuses, repeated entity appearances and common finding wording. They describe the indexed corpus and do not estimate national prevalence.

Web usage analytics count search, filter, source click, record view, entity view and zero-result interactions under hashed session IDs. Search text remains stored as submitted. These are development instrumentation events, not a representative user study or proof of usability.

<!-- page -->

# 10 Reliability deployment and reproducibility

The final automated suite contains 33 passing tests and one skipped optional live-source test. The new corpus tests verify all source hashes, chronology for every entity profile, TST2301 collisions, the reviewed Martin and Brown cross-source history and repeatable entity rebuilds.

The release verifier re-extracts all eight PDFs and confirms that every one of the 379 reconstructed rows equals the preserved intermediate output. It also confirms nine matching source hashes, 904 chronologically ordered profiles and five TST2301 contexts. Repeated legacy loading into a fresh database inserts 379 rows once and zero rows on the second run.

The frontend production build passes using the available Node 24 runtime. The project now declares the Vite-compatible Node range and includes a helper that selects a supported runtime. Node 16 cannot run the installed Vite 8 toolchain. Dependencies have a lockfile and the React plugin version is pinned.

| Capability | Final evidence status |
|---|---|
| SQLite API and corpus demonstration | Tested locally |
| Clean SQLite Alembic baseline | Tested |
| Production frontend compilation | Tested |
| PostgreSQL configuration and driver | Configured only |
| Docker and Nginx stack | Configured and source-reviewed only |
| Public HTTPS hosting | Not deployed |
| Independent human annotation review | Not completed |

The frontend Docker copy path was corrected to match Vite output. A Dockerfile is still not proof of a successful container run. SQLite supplies a simple local demonstration; PostgreSQL is appropriate for a later concurrent deployment once tested. The initial migration imports model metadata, so future schema evolution requires explicit versioned migration operations.

A frozen submission bundle includes the raw evidence, metadata, parsed output and database because these large generated artifacts are ignored by Git. Source code, labelled fixtures, decisions and reports are preserved with the release.

<!-- page -->

# 11 Engineering choices and contributions

We chose SQLAlchemy and a relational store because provenance, aliases and source records require explicit joins and uniqueness constraints. Adding Neo4j would introduce another store without solving a demonstrated query problem. We chose SQL substring search because the corpus has 599 rows; Elasticsearch is not required to demonstrate retrieval at this scale.

We omitted pgvector because no embedding model was retained. Adding vector infrastructure without an evaluated semantic method would increase complexity without a measured gain. We also omitted a chatbot, authentication and risk scoring because they do not establish the core acquisition, extraction and identity evidence.

The technical contribution is the working integration of heterogeneous public sources, table-aware extraction, validation, reproducible storage, recorded entity decisions and source-traceable histories. PyMuPDF, pdfplumber, RapidFuzz and relational queries are established techniques. Our project does not claim to invent these algorithms.

## Academic positioning

As a Data Engineering mini-project, the implementation demonstrates a complete bounded workflow with visible evidence and repeatable verification. As a Text Analytics application, it demonstrates normalization, candidate blocking and interpretable similarity matching. It is not a trained neural AI system.

As a research-paper foundation, it still needs larger independent labels, reviewer agreement, random and difficult negatives, broader layouts and ablation studies. The current scores support a local prototype evaluation with disclosed limits. They do not establish general performance on the CDSCO archive.

## What remains outside the frozen scope

The corpus is representative rather than complete. Company name clusters do not verify legal identity or collapse manufacturing facilities. Some plausible aliases remain unreviewed. Portal rows lack stable official identifiers. Revision relationships are not invented. PostgreSQL, Docker and public HTTPS require deployment validation, while primary labels still await independent human review.

These limits can be explained in the viva. They do not require adding more technologies to the bounded demonstration.

<!-- page -->

# 12 Demonstration and reproduction guide

Start the API from the project root using the project virtual environment. In another terminal start the frontend helper, which selects a supported Node runtime. Open http://127.0.0.1:5173.

1. Show 599 source rows and nine official sources on the overview.
2. Open a legacy event and identify its raw wording, PDF page, serial and hash.
3. Open a portal event and identify its reporting month and snapshot row position.
4. Search Martin and Brown and open the reviewed profile with twenty records spanning both source systems.
5. Read the aliases, observed addresses, review rationale and chronological history.
6. Open a product profile and distinguish raw wording from its cluster.
7. Search TST2301 and show all five product contexts.
8. Inspect unresolved suggestions and explain why a high similarity score alone is insufficient.
9. Compare regulatory analytics with the separate usage statistics.
10. Open the official source and match it to the preserved evidence.

For verification run scripts/verify_release.py and the backend pytest suite. For fresh offline reconstruction run scripts/load_database.py, scripts/restore_portal_snapshot.py and scripts/run_entity_resolution.py in that order. Use scripts/frontend.ps1 build to reproduce frontend compilation. Detailed commands are in COMPLETE_PROJECT_DOCUMENTATION.md.

## References and evidence

[1] RapidFuzz official similarity documentation. https://rapidfuzz.github.io/RapidFuzz/Usage/fuzz.html

[2] PyMuPDF official text extraction recipes. https://pymupdf.readthedocs.io/en/latest/recipes-text.html

[3] pdfplumber official project and table extraction documentation. https://github.com/jsvine/pdfplumber

[4] Sentence Transformers official semantic similarity documentation. https://sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html

[5] spaCy official training documentation. https://spacy.io/usage/training

Repository evidence includes docs/release-verification.json, docs/extraction-benchmark.md, data/samples/entity_resolution/corpus_pairs.jsonl and review_decisions.jsonl. External references describe library capabilities; project performance comes from the preserved local evidence and executable evaluations.
