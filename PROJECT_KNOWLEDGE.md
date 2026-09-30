# CDSCO Regulatory Intelligence — Project Knowledge Base

> **Repository:** `cdsco-regulatory-intelligence`  
> **Formal project title:** **Entity-Centric Drug Regulatory Intelligence from Fragmented CDSCO Alerts**  
> **Project type:** Honours Data Engineering Mini Project  
> **Primary domain:** Drug regulatory information / regulatory-quality intelligence  
> **Primary regulator:** Central Drugs Standard Control Organization (CDSCO), Government of India  
> **Last updated:** 2026-09-30  
> **Status:** Project scope and architecture defined; implementation in progress/planned.

---

## 0. How to use this document

This file is the single onboarding reference for:

- a new team member joining the project,
- an AI coding assistant,
- a project mentor/guide reviewing the technical direction,
- anyone who needs to understand the project without reading the full chat/project history.

An AI assistant should treat this document as the **project context and design contract** unless a newer decision is explicitly recorded elsewhere.

### Important project rule

This system **does not decide whether a medicine is safe or unsafe**.

It organizes, extracts, links, searches and analyzes information that has already been published by authorized regulatory sources.

The system must avoid unsupported conclusions such as:

- “Drug X is unsafe.”
- “Manufacturer Y makes bad medicines.”
- “This company has a poor safety score.”

Preferred wording:

- “This batch was listed in an official NSQ alert.”
- “These regulatory events were associated with this manufacturer in the collected CDSCO records.”
- “The system found N regulator-published events linked to this entity.”

---

# 1. Executive Summary

CDSCO publishes regulatory information through different webpages, monthly alerts, PDFs and regulatory notices. These records can include:

- Not of Standard Quality (NSQ) alerts,
- State NSQ alerts,
- spurious-drug alerts,
- revised alerts,
- recalls and other regulatory actions/notices.

The same real-world entity may appear differently across documents:

```text
ABC Pharmaceuticals Pvt. Ltd.
ABC Pharmaceuticals Private Limited
M/s ABC Pharmaceuticals Pvt Ltd
ABC Pharma Pvt. Ltd., Unit-II
```

A document-centric system treats these strings as separate values.

Our project aims to create an **entity-centric, time-aware regulatory intelligence system** that can:

1. collect official CDSCO records,
2. extract important entities and attributes,
3. normalize inconsistent formats,
4. resolve multiple mentions to canonical entities,
5. link regulatory events across time,
6. retain source provenance,
7. expose the result through search, analytics and a web interface.

The core transformation is:

```text
SCATTERED REGULATORY DOCUMENTS
            ↓
EXTRACTED REGULATORY RECORDS
            ↓
NORMALIZED ENTITIES
            ↓
ENTITY RESOLUTION
            ↓
TIME-AWARE REGULATORY HISTORY
            ↓
SEARCH + ANALYTICS + SOURCE TRACEABILITY
```

---

# 2. Project Motivation

## 2.1 The fundamental information problem

Regulators generally publish **events**:

```text
January NSQ alert
February State NSQ alert
Revised alert
Recall notice
Licence-related action
```

But users often want information about an **entity**:

```text
What regulatory events are associated with this drug?
What has been published about this manufacturer?
Has this batch appeared in any alert?
Was a previously published record later revised?
```

Therefore the core project idea is:

> **Regulators publish event-centric information; stakeholders need entity-centric information.**

---

## 2.2 Why this is a valid regulatory-data problem

CDSCO's public website exposes historical Drugs Consultative Committee records and regulatory alert material. The 69th Drugs Consultative Committee meeting, held on 24 June 2026, discussed information-sharing gaps between the Centre and States and recommended stronger publication/sharing of regulatory actions and NSQ-related data.

### Authoritative sources

- CDSCO official website:  
  https://cdsco.gov.in/

- CDSCO Drugs Consultative Committee (DCC) records:  
  https://cdsco.gov.in/opencms/opencms/en/Committees/DCC/

- CDSCO main Committees area:  
  https://cdsco.gov.in/opencms/opencms/en/Committees/

> Source accessibility must be rechecked during implementation because government page paths and layouts can change.

---

# 3. Problem Definition

## 3.1 Formal problem statement

Given heterogeneous drug regulatory records published through CDSCO-authorized sources:

1. identify mentions of drugs, manufacturers, batches and regulatory events,
2. extract relevant regulatory attributes,
3. normalize formatting differences,
4. determine when multiple records refer to the same real-world entity,
5. connect related events and revisions chronologically,
6. preserve the exact regulatory source supporting each derived record,
7. make the reconstructed regulatory history searchable and analyzable.

---

## 3.2 Core data-engineering difficulty

The challenge is **not merely scraping a webpage**.

The complete problem includes:

```text
Web crawling
    ↓
PDF/document collection
    ↓
Text/table extraction
    ↓
Cleaning
    ↓
Schema normalization
    ↓
Named entity extraction
    ↓
Entity resolution
    ↓
Event linking
    ↓
Temporal organization
    ↓
Database design
    ↓
Search/API layer
    ↓
Frontend and analytics
```

---

# 4. Project Objectives

The project aims to:

1. **Collect official regulatory data** from public CDSCO sources while retaining source metadata.
2. **Extract structured information** from HTML pages and regulatory PDF documents.
3. **Identify entities** such as drug/product, manufacturer, batch, dates, laboratory/authority, failure parameter and event type.
4. **Normalize textual variations** in entity names, dates, batch formats and common abbreviations.
5. **Resolve entity identity** when different records may refer to the same drug/manufacturer/batch.
6. **Link events temporally** to build entity-centric regulatory histories.
7. **Store curated information** in a structured, provenance-aware database.
8. **Expose backend APIs** for search and retrieval.
9. **Develop a web interface** for entity search, timelines and analytics.
10. **Evaluate NLP and entity-resolution quality** against manually verified records.

---

# 5. Project Scope

## 5.1 In scope

Initial implementation should prioritize:

- CDSCO public alert indexes,
- linked alert PDFs,
- CDSCO NSQ alerts,
- State NSQ alerts,
- revised alerts,
- selected other CDSCO notices when their structure is compatible.

The exact historical time window should be chosen after the first data audit.

---

## 5.2 Potential later extensions

Not required for the first semester version:

- additional State Drug Control authority websites,
- broader recall/licence-action integration,
- knowledge-graph representation,
- graph analytics,
- advanced document understanding,
- multilingual records,
- public dataset release,
- conference/dataset paper,
- larger-scale historical ingestion.

---

## 5.3 Explicitly out of scope

The project should **not** attempt to:

- diagnose medical conditions,
- recommend medicines,
- determine whether a medicine is clinically safe,
- predict future defective batches,
- declare a manufacturer unsafe,
- create unsupported “safety scores,”
- replace CDSCO or State regulator judgments,
- bypass CAPTCHA or anti-bot restrictions,
- scrape private/authenticated regulatory data.

---

# 6. Core Regulatory Concepts

## 6.1 Not of Standard Quality (NSQ)

An NSQ alert indicates that a **tested sample** failed one or more applicable quality requirements.

Important interpretation:

```text
Batch X being listed as NSQ
        ≠
Every batch of the medicine is defective
        ≠
Every product of the manufacturer is defective
        ≠
The active ingredient itself is unsafe
```

The system must retain batch/product/manufacturer granularity.

---

## 6.2 Other possible regulatory event types

Depending on available official data:

- `NSQ`
- `STATE_NSQ`
- `SPURIOUS`
- `REVISED_ALERT`
- `RECALL`
- `LICENCE_ACTION`
- `OTHER_REGULATORY_NOTICE`

The taxonomy must be based on actual observed CDSCO terminology rather than invented categories.

---

# 7. Conceptual Entity Model

Primary entities:

```text
MANUFACTURER
     │
     │ manufactures
     ▼
DRUG / PRODUCT
     │
     │ has
     ▼
BATCH / LOT
     │
     │ involved_in
     ▼
REGULATORY EVENT
     │
     ├── failure/reason
     ├── dates
     ├── testing authority/lab
     └── source document
```

Additional entities/attributes may include:

- drug strength,
- dosage form,
- manufacturing date,
- expiry date,
- manufacturer address,
- unit/location,
- state,
- testing laboratory,
- sample-drawing authority,
- failure parameter,
- publication date,
- alert type,
- alert revision relation.

---

# 8. Why Entity Resolution Matters

Named Entity Recognition answers:

> “What text span is a manufacturer?”

Entity resolution answers:

> “Do these two manufacturer mentions refer to the same real-world manufacturer?”

Example:

```text
ABC Pharmaceuticals Pvt. Ltd.
ABC Pharmaceuticals Private Limited
M/s ABC Pharmaceuticals Pvt Ltd.
ABC Pharmaceuticals Pvt Ltd., Unit-II
```

These may or may not represent the same canonical organization.

A reliable matching decision can use multiple signals:

```text
normalized company name
        +
address/location similarity
        +
legal suffix normalization
        +
drug/batch context
        +
string similarity
        +
embedding similarity
        ↓
entity-match confidence
```

No single similarity threshold should be treated as unquestionable ground truth.

---

# 9. Proposed Data Pipeline

## 9.1 Raw zone

Store source evidence without modification.

Examples:

```text
raw HTML
downloaded PDFs
alert title
source URL
document URL
retrieval timestamp
publication date
content hash
```

Purpose:

- reproducibility,
- debugging,
- auditability,
- reprocessing when extraction logic improves.

---

## 9.2 Standardized zone

Parsed document-level data:

```text
raw manufacturer text
raw drug text
raw batch value
parsed dates
event type
failure reason
document identifier
page/row location if available
```

---

## 9.3 Curated/entity zone

Canonicalized entities and linked histories:

```text
canonical manufacturer
manufacturer aliases
canonical drug/product
canonical batch
regulatory event
temporal relationship
revision relationship
source provenance
entity-resolution confidence
```

---

# 10. Proposed End-to-End Architecture

```text
                    CDSCO OFFICIAL SOURCES
                              │
                ┌─────────────┴─────────────┐
                │                           │
           HTML / INDEX PAGES           PDF DOCUMENTS
                │                           │
          Scrapy / Requests          PyMuPDF / pdfplumber
                └─────────────┬─────────────┘
                              │
                           RAW DATA
                              │
                           Pandas
                              │
                     TEXT PREPROCESSING
                              │
             ┌────────────────┼────────────────┐
             │                │                │
        NER / EXTRACTION   NORMALIZATION   CLASSIFICATION
           spaCy             Rules          scikit-learn
             │                │                │
             └────────────────┼────────────────┘
                              │
                     ENTITY RESOLUTION
                 RapidFuzz + SentenceTransformers
                              │
                      TEMPORAL / EVENT LINKING
                              │
                    PostgreSQL + pgvector
                              │
                           FastAPI
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
          Search           Analytics         Provenance
            │                 │                 │
            └─────────────────┼─────────────────┘
                              │
                         React + Vite
                              │
                       Web Analytics Logs
                              │
                         PostgreSQL
```

---

# 11. Technology Stack

## 11.1 Python

**Role:** Primary backend/data/NLP programming language.

Used for:

- scraping,
- PDF parsing,
- preprocessing,
- NLP,
- ML,
- entity resolution,
- backend APIs.

Official documentation:

https://docs.python.org/3/

---

## 11.2 Scrapy

**Role:** Structured web crawling and scraping framework.

Use it for:

- crawling CDSCO alert indexes,
- extracting alert metadata,
- discovering linked documents,
- building repeatable spiders and pipelines.

Official documentation:

https://docs.scrapy.org/en/latest/

---

## 11.3 Requests

**Role:** Simple HTTP requests and document downloading when a full Scrapy spider is unnecessary.

Documentation:

https://requests.readthedocs.io/

---

## 11.4 PyMuPDF

**Role:** Primary general PDF text extraction library.

Use for:

- extracting page text,
- reading document metadata,
- page-level parsing,
- initial PDF inspection.

Official documentation:

https://pymupdf.readthedocs.io/

Text extraction guide:

https://pymupdf.readthedocs.io/en/latest/recipes-text.html

---

## 11.5 pdfplumber

**Role:** Table/layout-oriented PDF extraction fallback/complement.

Use for:

- extracting tables,
- examining rows/columns,
- layout-aware parsing,
- visually debugging PDF extraction.

Official repository:

https://github.com/jsvine/pdfplumber

Important: pdfplumber works best on machine-generated PDFs; scanned PDFs may require a separate OCR fallback.

---

## 11.6 Pandas

**Role:** Tabular data manipulation and ETL.

Used for:

- cleaning extracted tables,
- normalizing fields,
- exploratory data analysis,
- joining/intermediate transformation,
- data-quality checks.

Official documentation:

https://pandas.pydata.org/docs/

---

## 11.7 NumPy

**Role:** Numerical operations used by the data/ML stack.

Official documentation:

https://numpy.org/doc/

---

## 11.8 spaCy

**Role:** Core NLP / named-entity and rule-based extraction toolkit.

Potential custom entity labels:

```text
DRUG
MANUFACTURER
BATCH
MFG_DATE
EXPIRY_DATE
LABORATORY
AUTHORITY
STATE
FAILURE_PARAMETER
REGULATORY_EVENT
```

Official documentation:

https://spacy.io/usage

spaCy 101:

https://spacy.io/usage/spacy-101

---

## 11.9 RapidFuzz

**Role:** High-performance fuzzy string matching for entity resolution.

Potential use cases:

- manufacturer-name similarity,
- normalized product-name comparison,
- address matching,
- alias candidate generation.

Official documentation:

https://rapidfuzz.github.io/RapidFuzz/

---

## 11.10 SentenceTransformers

**Role:** Semantic embeddings for similarity-based matching and search.

Potential use cases:

- semantic similarity between entity mentions,
- candidate entity matching,
- semantic search,
- retrieval experiments.

Official documentation:

https://sbert.net/

Quickstart:

https://www.sbert.net/docs/quickstart.html

### Important

The exact embedding model is **not locked yet**.

Model selection should be based on:

- the actual CDSCO text,
- latency,
- accuracy,
- model size,
- evaluation on manually labelled records.

---

## 11.11 scikit-learn

**Role:** Classical ML baselines and evaluation.

Potential use:

- text/event classification,
- baseline models,
- train/test evaluation,
- precision/recall/F1,
- confusion matrices.

Official documentation:

https://scikit-learn.org/

---

## 11.12 PostgreSQL

**Role:** Primary database.

Why PostgreSQL:

- structured regulatory entities,
- relationships,
- dates/temporal queries,
- strong integrity constraints,
- SQL analytics,
- compatibility with pgvector.

Official documentation:

https://www.postgresql.org/docs/

---

## 11.13 pgvector

**Role:** Vector/embedding storage and similarity search inside PostgreSQL.

This lets us avoid adding a separate vector database during the mini-project.

Official project:

https://github.com/pgvector/pgvector

---

## 11.14 FastAPI

**Role:** Python backend and REST API layer.

Responsibilities:

- search endpoints,
- entity detail endpoints,
- timelines,
- analytics,
- source/provenance retrieval,
- frontend/backend integration.

Official documentation:

https://fastapi.tiangolo.com/

Tutorial:

https://fastapi.tiangolo.com/tutorial/

---

## 11.15 React

**Role:** Main web frontend.

Potential UI:

- global search,
- manufacturer page,
- drug page,
- batch page,
- regulatory-event view,
- entity timeline,
- analytics dashboard,
- source-document links.

Official documentation:

https://react.dev/

Learning guide:

https://react.dev/learn

---

## 11.16 Vite

**Role:** React development/build tooling.

Official documentation:

https://vite.dev/

Getting started:

https://vite.dev/guide/

---

## 11.17 Visualization library

Current options:

- Recharts: https://recharts.org/
- Plotly JavaScript: https://plotly.com/javascript/

**Not permanently locked.**

Use whichever integrates best with the final analytics requirements.

---

## 11.18 Docker / Docker Compose

**Role:** Reproducible local deployment.

Expected services:

```text
frontend
backend
postgres
```

Official documentation:

https://docs.docker.com/

Docker Compose:

https://docs.docker.com/compose/

---

## 11.19 Git

**Role:** Source version control.

Official documentation:

https://git-scm.com/doc

---

## 11.20 GitHub

**Role:** Repository hosting, collaboration, issues, pull requests and project history.

Official documentation:

https://docs.github.com/en/repositories

---

# 12. Technologies Deliberately Not Required Initially

## 12.1 Neo4j

The domain is graph-like, but introducing both PostgreSQL and Neo4j in the first semester would create unnecessary infrastructure.

Potential future extension:

```text
PostgreSQL curated entities
        ↓
Knowledge graph export
        ↓
Neo4j / graph analytics
```

Neo4j documentation:

https://neo4j.com/docs/

---

## 12.2 Elasticsearch / OpenSearch

Not required initially.

We expect:

```text
PostgreSQL relational queries
+
PostgreSQL full-text capabilities
+
pgvector semantic similarity
```

to be adequate for the project scale.

---

## 12.3 LLM APIs

GPT/Gemini/Claude APIs are **not core dependencies**.

Why:

- extraction must be reproducible,
- evaluation must be meaningful,
- we do not want the research contribution to be “send document to an LLM.”

LLMs may later be used as:

- an experimental baseline,
- a summarization layer,
- a comparison system,

but should not become a hidden source of regulatory truth.

---

# 13. Proposed Repository Structure

```text
cdsco-regulatory-intelligence/
│
├── README.md
├── PROJECT_KNOWLEDGE.md
├── .gitignore
├── .env.example
├── requirements.txt
├── docker-compose.yml
├── LICENSE                         # only when licensing is intentionally chosen
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── search.py
│   │   │   │   ├── drugs.py
│   │   │   │   ├── manufacturers.py
│   │   │   │   ├── batches.py
│   │   │   │   ├── events.py
│   │   │   │   ├── analytics.py
│   │   │   │   └── sources.py
│   │   │   └── dependencies.py
│   │   │
│   │   ├── scraper/
│   │   │   ├── spiders/
│   │   │   ├── parsers/
│   │   │   ├── pipelines/
│   │   │   └── settings.py
│   │   │
│   │   ├── extraction/
│   │   │   ├── pdf_text.py
│   │   │   ├── pdf_tables.py
│   │   │   ├── html_parser.py
│   │   │   └── document_router.py
│   │   │
│   │   ├── preprocessing/
│   │   │   ├── text_cleaning.py
│   │   │   ├── date_normalization.py
│   │   │   ├── batch_normalization.py
│   │   │   └── manufacturer_normalization.py
│   │   │
│   │   ├── nlp/
│   │   │   ├── entities.py
│   │   │   ├── rules.py
│   │   │   ├── event_classifier.py
│   │   │   └── models/
│   │   │
│   │   ├── entity_resolution/
│   │   │   ├── candidate_generation.py
│   │   │   ├── string_similarity.py
│   │   │   ├── semantic_similarity.py
│   │   │   ├── resolver.py
│   │   │   └── evaluation.py
│   │   │
│   │   ├── temporal/
│   │   │   ├── event_linking.py
│   │   │   └── revisions.py
│   │   │
│   │   ├── analytics/
│   │   │   ├── regulatory_metrics.py
│   │   │   └── web_events.py
│   │   │
│   │   ├── database/
│   │   │   ├── models/
│   │   │   ├── repositories/
│   │   │   ├── migrations/
│   │   │   └── session.py
│   │   │
│   │   ├── schemas/
│   │   ├── core/
│   │   └── utils/
│   │
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── fixtures/
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── features/
│   │   ├── hooks/
│   │   ├── utils/
│   │   └── App.jsx
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── data/
│   ├── raw/
│   │   ├── html/
│   │   └── pdf/
│   ├── interim/
│   ├── processed/
│   ├── curated/
│   └── samples/
│
├── notebooks/
│   ├── 01_data_audit.ipynb
│   ├── 02_pdf_extraction.ipynb
│   ├── 03_entity_extraction.ipynb
│   ├── 04_entity_resolution.ipynb
│   └── 05_evaluation.ipynb
│
├── scripts/
│   ├── scrape_alerts.py
│   ├── process_documents.py
│   ├── run_entity_resolution.py
│   └── load_database.py
│
├── docs/
│   ├── architecture/
│   ├── literature/
│   ├── presentations/
│   ├── project-report/
│   ├── decisions/
│   └── data-dictionary.md
│
└── .github/
    ├── ISSUE_TEMPLATE/
    └── workflows/
```

---

# 14. Repository File Responsibilities

## `README.md`

Short public/project landing page:

- project title,
- 5–10 line overview,
- setup instructions,
- screenshots,
- current status,
- contributors.

Keep it readable.

---

## `PROJECT_KNOWLEDGE.md`

This document.

Purpose:

> exhaustive project context for developers, AI assistants and new team members.

---

## `docs/decisions/`

Use Architecture Decision Records (ADRs) or simple decision notes.

Example:

```text
docs/decisions/
├── 001-postgresql-over-mongodb.md
├── 002-no-neo4j-in-mvp.md
├── 003-fastapi-backend.md
└── 004-entity-resolution-strategy.md
```

Each should answer:

```text
What decision was made?
Why?
What alternatives were considered?
What are the consequences?
```

---

# 15. Suggested Database Model

## 15.1 `manufacturers`

```text
id
canonical_name
normalized_name
canonical_address
created_at
updated_at
```

---

## 15.2 `manufacturer_aliases`

```text
id
manufacturer_id
alias_text
normalized_alias
source_record_id
confidence
```

---

## 15.3 `drugs`

```text
id
canonical_name
normalized_name
strength
dosage_form
```

---

## 15.4 `drug_aliases`

```text
id
drug_id
alias_text
normalized_alias
source_record_id
```

---

## 15.5 `batches`

```text
id
batch_number
normalized_batch_number
drug_id
manufacturer_id
manufacturing_date
expiry_date
```

---

## 15.6 `regulatory_events`

```text
id
event_type
event_date
publication_date
drug_id
manufacturer_id
batch_id
failure_reason_raw
failure_reason_normalized
authority
laboratory
source_document_id
revision_of_event_id
```

---

## 15.7 `source_documents`

```text
id
source_url
document_url
document_type
alert_title
publication_date
retrieved_at
content_hash
local_path
```

---

## 15.8 `entity_matches`

Useful for audit/evaluation.

```text
id
entity_type
left_record_id
right_record_id
name_similarity
semantic_similarity
context_similarity
combined_score
predicted_match
manual_label
resolution_method
```

---

## 15.9 `web_analytics_events`

```text
id
session_id
event_type
query_text
entity_type
entity_id
result_count
timestamp
metadata_json
```

Potential event types:

```text
SEARCH
ZERO_RESULT_SEARCH
ENTITY_VIEW
FILTER_APPLIED
SOURCE_CLICK
TIMELINE_VIEW
```

---

# 16. Proposed API Surface

Initial REST endpoints may include:

```http
GET /health

GET /api/search?q=paracetamol
GET /api/search?q=ABC+Pharma&type=manufacturer

GET /api/drugs/{drug_id}
GET /api/drugs/{drug_id}/events

GET /api/manufacturers/{manufacturer_id}
GET /api/manufacturers/{manufacturer_id}/events

GET /api/batches/{batch_id}
GET /api/batches/{batch_id}/events

GET /api/events/{event_id}
GET /api/sources/{source_id}

GET /api/analytics/events
GET /api/analytics/failure-reasons
GET /api/analytics/timeline
```

API naming can change during implementation.

---

# 17. Proposed Frontend Pages

## 17.1 Home / global search

Search by:

- drug,
- manufacturer,
- batch.

---

## 17.2 Search results

Display:

- matched canonical entity,
- alias/why matched,
- entity type,
- number of linked regulatory events,
- most recent event date.

---

## 17.3 Drug page

Potential sections:

```text
Canonical drug name
Known aliases
Associated manufacturers
Associated batches
Regulatory event timeline
Failure/event distribution
Official source links
```

---

## 17.4 Manufacturer page

Potential sections:

```text
Canonical manufacturer
Known aliases
Known unit/address variants
Associated drug products
Associated batches
Regulatory timeline
Original CDSCO sources
```

---

## 17.5 Batch page

Potential sections:

```text
Batch number
Drug/product
Manufacturer
Manufacturing/expiry date
Associated regulatory event(s)
Failure information
Source document
```

---

## 17.6 Regulatory event page

Display:

- event type,
- raw extracted values,
- canonical linked entities,
- dates,
- failure reason,
- source,
- revision relationship if applicable.

---

## 17.7 Analytics page

Possible charts:

- events by year/month,
- event type distribution,
- failure-reason distribution,
- top recurring normalized entities,
- document/source statistics.

**Important:** raw event counts must not be presented as direct safety rankings.

---

# 18. Text Analytics / NLP Strategy

## 18.1 Preprocessing

Potential operations:

- Unicode normalization,
- whitespace normalization,
- punctuation normalization,
- date normalization,
- legal company suffix normalization,
- abbreviation normalization,
- batch-number cleanup,
- casing normalization where appropriate.

Do **not** blindly remove punctuation if punctuation is meaningful in batch codes or drug strengths.

---

## 18.2 Entity extraction

Potential approaches:

### Rule/pattern-based extraction

Useful for:

- dates,
- batch-number labels,
- strength patterns,
- “Mfg.” / “Exp.” fields,
- table columns.

### spaCy NER / custom pipeline

Useful for:

- manufacturer names,
- drug/product names,
- organizations,
- testing laboratories,
- authorities,
- free-text failure reasons.

The final solution may be hybrid rather than purely ML-based.

---

## 18.3 Event classification

Potential labels:

```text
NSQ
STATE_NSQ
SPURIOUS
REVISED_ALERT
RECALL
OTHER
```

Possible baselines:

- keyword/rule system,
- TF-IDF + Logistic Regression,
- TF-IDF + Linear SVM,
- embedding classifier.

Use the simplest method that achieves reliable results.

---

# 19. Entity Resolution Strategy

## 19.1 Stage 1 — Deterministic normalization

Examples:

```text
"Pvt." → "Private"
"Ltd." → "Limited"
"M/s" → removed/normalized
multiple spaces → one space
punctuation → standardized
```

But retain the original raw string separately.

---

## 19.2 Stage 2 — Candidate generation

Avoid comparing every entity with every other entity.

Candidates can be generated by:

- initial tokens,
- state/location,
- normalized manufacturer name,
- product context,
- approximate string blocks.

---

## 19.3 Stage 3 — String similarity

RapidFuzz features may include:

```text
ratio
partial_ratio
token_sort_ratio
token_set_ratio
```

Exact choice must be validated on labelled examples.

---

## 19.4 Stage 4 — Semantic similarity

SentenceTransformer embeddings can compare textual/contextual representations.

Example candidate representation:

```text
manufacturer name + address + associated product context
```

---

## 19.5 Stage 5 — Combined decision

Possible conceptual scoring:

```text
match_score =
    w1 * normalized_name_similarity
  + w2 * address_similarity
  + w3 * semantic_similarity
  + w4 * contextual_overlap
```

This is only a conceptual design.

Weights/thresholds must be determined empirically.

---

## 19.6 Stage 6 — Human-verifiable output

For uncertain matches, the system should ideally preserve:

```text
candidate A
candidate B
individual feature scores
combined score
match decision
source evidence
```

This makes entity resolution explainable and evaluatable.

---

# 20. Temporal Linking

A regulatory entity may have multiple events:

```text
2024-01 → NSQ
2024-02 → revised alert
2024-03 → recall
2025-06 → another batch listed in NSQ
```

The database must distinguish:

- `event_date`,
- `publication_date`,
- `retrieval_date`.

These dates are not interchangeable.

Potential relationships:

```text
EVENT_A revised_by EVENT_B
EVENT_C relates_to BATCH_X
EVENT_C relates_to MANUFACTURER_Y
EVENT_C published_in SOURCE_Z
```

---

# 21. Provenance Requirements

Every curated fact should be traceable back to evidence.

Minimum provenance:

```text
source URL
document URL
alert title
publication date
retrieval timestamp
source document ID
page/row if available
raw source text
```

A user should be able to move:

```text
Canonical entity
    ↓
Regulatory event
    ↓
Extracted source record
    ↓
Original CDSCO document/page
```

Provenance is a core feature, not an optional add-on.

---

# 22. Evaluation Plan

## 22.1 Ground truth

Create a manually verified sample of records.

Annotate:

- entity spans,
- entity types,
- normalized values,
- same-entity/different-entity pairs,
- event type,
- revision links where applicable.

Store annotation guidelines in:

```text
docs/annotation-guidelines.md
```

---

## 22.2 NER / extraction metrics

Use:

```text
Precision
Recall
F1-score
```

Also track field-level exact/normalized correctness where appropriate.

---

## 22.3 Entity-resolution metrics

Use:

```text
Pairwise Precision
Pairwise Recall
Pairwise F1
```

Optionally evaluate:

- precision at different thresholds,
- false-positive categories,
- false-negative categories.

False positive entity merges are especially important because merging unrelated manufacturers can create misleading regulatory histories.

---

## 22.4 Event classification

Possible metrics:

```text
Accuracy
Macro Precision
Macro Recall
Macro F1
Confusion Matrix
```

Use macro metrics when class counts are imbalanced.

---

## 22.5 Data-engineering quality metrics

Potential measures:

- ingestion success rate,
- PDF parse success rate,
- fields missing per document type,
- duplicate reduction,
- provenance completeness,
- percentage of records requiring manual review.

---

## 22.6 System quality

Potential measures:

- API correctness,
- query latency,
- frontend usability,
- zero-result searches,
- broken source-link rate.

---

# 23. Web Analytics Strategy

We do **not** have access to CDSCO's private website analytics.

Web Analytics is applied to **our own portal**.

Track events such as:

```text
SEARCH
ENTITY_VIEW
SOURCE_CLICK
FILTER_APPLIED
ZERO_RESULT_SEARCH
```

Potential metrics:

- number of searches,
- unique sessions,
- most searched entity types,
- searches with no result,
- source-document click-through rate,
- frequently used filters.

Web analytics should help improve our own system, not make claims about public behavior on CDSCO's website.

---

# 24. Git / GitHub Workflow

## 24.1 Main branches

Recommended:

```text
main
develop
```

For a small team, `develop` can be omitted if it becomes unnecessary.

Feature branches:

```text
feature/cdsco-scraper
feature/pdf-parser
feature/entity-extraction
feature/entity-resolution
feature/backend-search
feature/frontend-timeline
```

---

## 24.2 Commit style

Examples:

```text
feat: add CDSCO alert index spider
fix: normalize manufacturer legal suffixes
test: add entity-resolution fixtures
docs: document raw data schema
refactor: split PDF parsing pipeline
```

---

## 24.3 Pull requests

Important changes should ideally enter `main` through pull requests so team members can review:

- schema migrations,
- entity-resolution changes,
- scraper changes,
- API breaking changes.

---

# 25. `.gitignore` Guidance

Do not commit:

```text
.env
.env.*
.venv/
venv/
__pycache__/
*.pyc
node_modules/
frontend/dist/

data/raw/*
data/interim/*
large downloaded PDFs

database dumps
model checkpoints (unless intentionally versioned)
API keys
passwords
private credentials
```

Use placeholder files like `.gitkeep` if folder structure must be retained.

Safe sample records may go into:

```text
data/samples/
```

---

# 26. Environment / Secret Management

Commit:

```text
.env.example
```

Do not commit:

```text
.env
```

Possible environment variables:

```env
DATABASE_URL=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=

API_HOST=
API_PORT=

SCRAPER_USER_AGENT=
DATA_DIR=

FRONTEND_API_BASE_URL=
```

If external model/API credentials are added later, they must also remain in secrets/environment variables.

---

# 27. Testing Strategy

## Unit tests

Test individual functions:

```text
date normalization
manufacturer normalization
batch normalization
string scoring
event classification
document parser functions
```

---

## Integration tests

Test:

```text
document → parsed record
record → database
database → API
API → frontend
```

---

## Regression tests

Keep representative problematic documents/records as fixtures.

If a parser bug is fixed, add a test so it does not return.

---

# 28. Data Collection Ethics and Constraints

1. Use only public/authorized data.
2. Respect website terms and technical limits.
3. Use rate limiting and polite crawling.
4. Do not attempt CAPTCHA bypass.
5. Cache/download once when possible instead of repeatedly hitting government servers.
6. Record retrieval timestamps.
7. Keep original documents for reproducibility.
8. Do not silently alter regulator-published wording.

---

# 29. Current Implementation Schedule

## July — Second fortnight

- problem identification,
- domain study,
- preliminary literature review.

## August — First fortnight

- finalize problem statement,
- objectives and scope,
- identify authoritative CDSCO data sources.

## August — Second fortnight

- detailed literature review,
- data feasibility,
- schema design,
- initial scraping pipeline.

## September — First fortnight

- CDSCO data collection,
- PDF/text extraction,
- cleaning and structured raw dataset.

## September — Second fortnight

- entity extraction,
- regulatory-field extraction,
- preliminary evaluation.

## October — First fortnight

- entity normalization,
- entity resolution,
- duplicate detection,
- temporal/event linking.

## October — Second fortnight

- PostgreSQL integration,
- FastAPI backend,
- search APIs,
- analytics/provenance.

## November — First fortnight

- React frontend,
- backend integration,
- system testing,
- evaluation,
- documentation,
- prototype deployment.

---

# 30. Expected End-of-Term Deliverable

By the end of the first term, the project should provide a working prototype that:

- collects selected CDSCO regulatory records,
- parses HTML/PDF data,
- extracts regulatory entities,
- normalizes and resolves entity identity,
- links related regulatory events over time,
- stores structured data with provenance,
- provides backend APIs,
- supports entity search,
- displays regulatory histories,
- provides basic analytics,
- evaluates extraction/entity-resolution performance.

---

# 31. Research Questions

Primary question:

> **How effectively can heterogeneous CDSCO regulatory records be transformed from document-centric publications into an entity-centric, time-aware and provenance-preserving representation of drugs, manufacturers, batches and regulatory events?**

Possible secondary questions:

1. How accurately can key entities be extracted from CDSCO documents?
2. How accurately can manufacturer/drug naming variations be resolved?
3. How much duplication/fragmentation is reduced after entity resolution?
4. How can revised alerts be connected to earlier records?
5. What new longitudinal queries become possible after entity-centric integration?
6. Which entity-resolution signals contribute most to reliable matching?

---

# 32. Research Contribution We Should Aim For

Weak contribution:

> “We scraped CDSCO and made a dashboard.”

Stronger contribution:

> “We designed and evaluated a reproducible pipeline for extracting and reconciling heterogeneous CDSCO drug-regulatory records into canonical entities and time-aware regulatory histories with source provenance.”

Potential paper-oriented contributions:

- curated CDSCO regulatory dataset,
- entity annotation dataset,
- manufacturer/entity-resolution benchmark,
- comparison of matching techniques,
- temporal regulatory record linking,
- provenance-aware regulatory intelligence architecture.

Any claim of novelty must be supported by a systematic literature/prior-art review before publication.

---

# 33. Risks and Mitigations

## Risk: PDF formats vary significantly

Mitigation:

- document-type detection,
- multiple parsers,
- store raw data,
- manual fallback for rare layouts.

---

## Risk: scanned PDFs

Mitigation:

- identify them during data audit,
- use OCR only when necessary,
- measure OCR quality separately.

---

## Risk: false entity merges

Mitigation:

- conservative thresholds,
- multiple similarity features,
- confidence scores,
- manual review for ambiguous cases,
- preserve original mentions.

---

## Risk: dataset too small for training custom NLP models

Mitigation:

- hybrid rule + pretrained NLP approach,
- weak supervision/manual annotation,
- classical baselines,
- treat extraction quality—not model novelty—as the research focus.

---

## Risk: project scope becomes too large

Mitigation:

Prioritize:

```text
NSQ
+
State NSQ
+
Revised alerts
```

before extending to all regulatory categories.

---

## Risk: government website changes

Mitigation:

- scraper tests,
- source abstraction,
- retain downloaded documents,
- record source metadata,
- avoid hardcoding presentation-layer details when possible.

---

# 34. Decisions Already Made

### Locked

```text
Project topic:
Entity-Centric Drug Regulatory Intelligence from Fragmented CDSCO Alerts

Main language:
Python

Backend:
FastAPI

Database:
PostgreSQL

Vector support:
pgvector

Frontend:
React + Vite

Scraping:
Scrapy + Requests

PDF extraction:
PyMuPDF + pdfplumber

NLP:
spaCy

Entity resolution:
rule-based normalization + RapidFuzz + SentenceTransformers

ML/evaluation:
scikit-learn

Version control:
Git + GitHub

Containerization:
Docker / Docker Compose
```

---

# 35. Decisions Not Yet Locked

Do not assume these without evaluation:

```text
exact NER model
exact SentenceTransformer model
exact string-similarity metric
entity-match threshold
classification algorithm
OCR engine
cloud provider
deployment host
graph database
knowledge-graph implementation
full historical date range
complete list of CDSCO document categories
```

---

# 36. Primary External Sources

## CDSCO

Official CDSCO:

https://cdsco.gov.in/

DCC meetings:

https://cdsco.gov.in/opencms/opencms/en/Committees/DCC/

Committees:

https://cdsco.gov.in/opencms/opencms/en/Committees/

During implementation, record the exact production URLs for:

- alert index,
- NSQ archive,
- State NSQ archive,
- revised alert documents,
- any recall/other regulatory sources included in scope.

---

# 37. Official Technology References

| Technology | Official source |
|---|---|
| Python | https://docs.python.org/3/ |
| Scrapy | https://docs.scrapy.org/en/latest/ |
| Requests | https://requests.readthedocs.io/ |
| PyMuPDF | https://pymupdf.readthedocs.io/ |
| pdfplumber | https://github.com/jsvine/pdfplumber |
| Pandas | https://pandas.pydata.org/docs/ |
| NumPy | https://numpy.org/doc/ |
| spaCy | https://spacy.io/usage |
| RapidFuzz | https://rapidfuzz.github.io/RapidFuzz/ |
| SentenceTransformers | https://sbert.net/ |
| scikit-learn | https://scikit-learn.org/ |
| PostgreSQL | https://www.postgresql.org/docs/ |
| pgvector | https://github.com/pgvector/pgvector |
| FastAPI | https://fastapi.tiangolo.com/ |
| React | https://react.dev/ |
| Vite | https://vite.dev/ |
| Docker | https://docs.docker.com/ |
| Git | https://git-scm.com/doc |
| GitHub | https://docs.github.com/en/repositories |

---

# 38. Suggested First Development Tasks

A new developer should **not start by building the frontend**.

Recommended sequence:

### Task 1 — data audit

Collect a small sample:

```text
10–20 CDSCO alert documents
multiple months
multiple alert types
at least one revised alert
```

Document:

- formats,
- fields,
- parsing problems,
- naming variations.

Output:

```text
docs/data-audit.md
```

---

### Task 2 — source ingestion prototype

Build:

```text
alert index → document metadata → PDF download
```

Do not yet optimize for every historical page.

---

### Task 3 — raw schema

Store:

```text
source URL
document URL
alert title
publication date
file hash
retrieval date
local path
```

---

### Task 4 — document parsing benchmark

Compare:

```text
PyMuPDF
pdfplumber
```

on representative CDSCO PDFs.

Record which works best for which document type.

---

### Task 5 — create labelled mini dataset

Manually label a small number of records.

This becomes the first evaluation set.

---

### Task 6 — entity normalization baseline

Before embeddings, build deterministic normalization and RapidFuzz baselines.

Measure them.

---

### Task 7 — database + API

Only after data shape is reasonably understood.

---

### Task 8 — frontend

Once API contracts stabilize.

---

# 39. Definition of Done for MVP

The MVP is complete when:

- [ ] official CDSCO data can be collected reproducibly,
- [ ] raw documents are preserved,
- [ ] structured records are extracted,
- [ ] at least the core entities are identified,
- [ ] manufacturer/drug/batch normalization is implemented,
- [ ] entity-resolution logic is evaluated,
- [ ] temporal regulatory events can be retrieved,
- [ ] PostgreSQL stores curated records,
- [ ] source provenance is available,
- [ ] FastAPI exposes search/entity/event endpoints,
- [ ] React can search and display an entity timeline,
- [ ] evaluation metrics are documented,
- [ ] limitations are explicitly stated,
- [ ] the project does not make unsupported medical safety claims.

---

# 40. AI Assistant Handoff Instructions

When an AI assistant works on this repository:

1. Read this file first.
2. Do not silently change the project scope.
3. Preserve provenance fields when changing data models.
4. Never generate code that labels an entire drug/manufacturer as “safe” or “unsafe.”
5. Prefer simple, testable pipelines before adding complex models.
6. Do not introduce new databases/frameworks without explaining why the existing stack is insufficient.
7. Before changing an extraction rule, test it against representative CDSCO documents.
8. Before changing entity-resolution logic, evaluate both false merges and missed matches.
9. Keep original raw text alongside normalized values.
10. Treat CDSCO/authorized regulatory documents as the factual source of regulatory events.
11. Never bypass CAPTCHA/anti-bot systems.
12. Do not commit secrets or large raw datasets to Git.
13. Add/update tests when fixing parser or normalization bugs.
14. If a decision changes, record it under `docs/decisions/`.
15. Update this knowledge file when architecture/scope decisions materially change.

---

# 41. Glossary

### CDSCO
Central Drugs Standard Control Organization.

### NSQ
Not of Standard Quality.

### NER
Named Entity Recognition — identifying spans such as drug/manufacturer/batch from text.

### Entity Resolution
Determining whether different records refer to the same real-world entity.

### Canonical Entity
The normalized identity used to represent multiple source mentions.

### Alias
A source-specific name linked to a canonical entity.

### Regulatory Event
An official regulatory record/action associated with an entity.

### Provenance
Information showing the exact source from which a fact/record was derived.

### Temporal Linking
Connecting regulatory events in chronological/revision relationships.

### Embedding
A numerical representation of text used for semantic similarity/search.

### pgvector
PostgreSQL extension for vector similarity operations.

---

# 42. Final Mental Model

The project is **not**:

```text
PDF scraper
```

and it is **not**:

```text
drug safety prediction
```

It is:

```text
Authoritative regulatory documents
              ↓
         Data engineering
              ↓
       Text information extraction
              ↓
         Entity resolution
              ↓
       Temporal event linking
              ↓
       Provenance-aware database
              ↓
 Searchable regulatory intelligence
```

The most important one-line description is:

> **We reconstruct what authorized regulators have reported about specific drugs, manufacturers and batches across fragmented records and time.**
