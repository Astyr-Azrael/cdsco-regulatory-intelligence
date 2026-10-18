# Data dictionary

## Provenance tables

`source_documents` represents one preserved official PDF or structured-source snapshot. It stores source URLs, title/type, publication/retrieval date, raw path, MIME type, page count, extraction status and unique SHA-256.

`ingestion_runs` stores operational status, parser version, timestamps and record counts seen, inserted and updated.

`parsed_regulatory_records` represents one source row. `raw_*` fields preserve regulator-published values. Parsed dates contain normalized `YYYY-MM` values only when supported. Page, row, bounding box, raw cells/text, parser version, warnings and parse status preserve extraction evidence.

## Entity tables

`canonical_manufacturers` contains organization name clusters and primary source-reviewed links with preferred display name, normalized key and resolution status.

`manufacturer_aliases` links one record to a canonical manufacturer and stores original mention, split display name/address, normalized values, method, score and review status.

`canonical_drugs` contains conservative product clusters with preferred name, normalized key, strength signals, dosage forms and resolution status.

`drug_aliases` links one record to a canonical product and preserves original wording, strength/form signals, method, score and review status.

`entity_matches` contains RapidFuzz candidate-pair evidence: both mentions/keys, method, score, decision, review status and features. `REVIEW` never means a canonical merge. Explicit source-bound MATCH decisions with PRIMARY_SOURCE_REVIEW status are reapplied by the entity builder. These are primary assistant source reviews, not independently verified legal identities. Scores represent string similarity rather than probability.

## Usage table

`web_usage_events` stores an anonymous hashed session ID, allowed event type, optional entity reference, bounded query text, filters, metadata and timestamp. Usage analytics remain separate from regulatory analytics.

Batch contexts are returned by the API using product, manufacturer and observed site address; there is no globally unique batch table. Portal date precision is month, not an inferred publication day. Twelve unknown manufacturer placeholders remain raw values without identity aliases.

Every alias remains traceable through its source record to the official URL, hash and page/row or portal position.
