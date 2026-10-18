# Final architecture and workflow

Updated 19 October 2026. Solid schema relationships below correspond to implemented foreign keys. Match and usage references are logical keys only.

## Processing architecture

```mermaid
flowchart LR
 A[Official legacy index] --> B[Bounded download and preserved HTML PDFs]
 C[Official public portal] --> D[Validated preserved JSON]
 B --> E[Page text coordinates and layout tables]
 E --> F[Category parsers and validation]
 D --> F
 F --> G[(Source documents and parsed records)]
 G --> H[Normalized organization and product clusters]
 H --> I[Blocked RapidFuzz proposals]
 I --> J[Unreviewed suggestions]
 I --> K[Versioned source review decisions]
 K --> L[Apply accepted links and retain rejections]
 H --> L
 L --> M[(Canonical entities and aliases)]
 G --> N[FastAPI record and source APIs]
 M --> O[Chronological entity history APIs]
 N --> P[React portal]
 O --> P
 P --> Q[Separate application usage events]
```

The live SQLite demo has 599 source rows. PostgreSQL uses the same SQLAlchemy models but execution remains untested. RapidFuzz proposals alone never create a reviewed identity.

## Implemented relational schema

```mermaid
erDiagram
 SOURCE_DOCUMENTS ||--o{ PARSED_REGULATORY_RECORDS : contains
 PARSED_REGULATORY_RECORDS ||--o| MANUFACTURER_ALIASES : supports
 PARSED_REGULATORY_RECORDS ||--o| DRUG_ALIASES : supports
 CANONICAL_MANUFACTURERS ||--o{ MANUFACTURER_ALIASES : groups
 CANONICAL_DRUGS ||--o{ DRUG_ALIASES : groups
```

entity_matches stores string comparison keys and evidence JSON. It has no foreign key to canonical entities. ingestion_runs is a process log without a run-to-source association table. web_usage_events stores logical entity type/ID references rather than enforced entity foreign keys.

## Temporal and batch semantics

Histories join aliases to records and sources, then sort by date, document, serial and record ID. Portal date precision is month. Organization histories aggregate names while preserving observed manufacturing addresses. Batch contexts use product, organization and observed address; no globally unique batch table is asserted.

The old temporal helper files are not on the production path. Revision linking remains absent unless future evidence supports an explicit relation.
