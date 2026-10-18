# Annotation guidelines

## Row extraction

Annotate directly from a rendered official source before viewing parser output. Record document hash/filename, page, visible serial row, alert category and every supported field. Preserve capitalization and punctuation where legible; use `null` when the source does not state a value. Mark unreadable text for review instead of guessing.

Complete a second review for publishable evaluation sets. Record annotator/reviewer status and disagreement notes. The current unseen 11-row set has primary review complete and awaits a second human review.

## Entity pairs

Label `MATCH` only when evidence supports the same real-world manufacturer or the same product including relevant strength/form. Label `NO_MATCH` when legal identity, active composition, strength or dosage form differs. Use `AMBIGUOUS` when evidence is insufficient; ambiguous pairs must remain unresolved.

For each pair retain both original mentions, entity type, available address/context, label, review status and concise rationale. Do not use a fuzzy score as the label. Reviewers should see source context and decide independently before comparing decisions.

## Revision links

Link a revised alert to an earlier record only when the publication explicitly identifies the earlier record or a sufficiently specific combination of source title/date, product, batch and corrected field supports the link. Preserve both events and the evidence for the relationship.
