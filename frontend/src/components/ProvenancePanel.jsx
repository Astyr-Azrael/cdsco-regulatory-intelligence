import React from 'react'
import { Icon } from './Icons.jsx'
import { SourceLink } from './SourceLink.jsx'

export function ProvenancePanel({ record }) {
  return <section className="provenance-panel">
    <div className="panel-title-row"><div><span className="section-kicker">Source provenance</span><h2>Trace this record to CDSCO</h2></div><span className="verified-label"><Icon name="check" size={15}/>Source text checked</span></div>
    <div className="provenance-chain">
      <div><span>Canonical event</span><strong>{record.id}</strong></div><i>linked from</i>
      <div><span>Extracted record</span><strong>Page {record.sourcePage} · row {record.sourceRow}</strong></div><i>published in</i>
      <div><span>Official document</span><strong>{record.source.shortTitle}</strong></div>
    </div>
    <dl className="definition-grid"><div><dt>Official document title</dt><dd>{record.source.title}</dd></div><div><dt>Source location</dt><dd>Page {record.sourcePage}, table row {record.sourceRow}; extracted text lines {record.sourceLines}</dd></div><div><dt>Retrieval date</dt><dd>{record.source.retrievalDate}</dd></div><div><dt>Extraction status</dt><dd>{record.extractionStatus}</dd></div></dl>
    <div className="panel-actions"><SourceLink source={record.source}/><a className="subtle-link" href={record.source.indexUrl} target="_blank" rel="noreferrer">View CDSCO alerts index</a></div>
  </section>
}
