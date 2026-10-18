import React from 'react'
import { Icon } from './Icons.jsx'
import { SourceLink } from './SourceLink.jsx'

export function ProvenancePanel({ record }) {
  return <section className="provenance-panel">
    <div className="panel-title-row"><div><span className="section-kicker" title="The official regulatory source supporting the displayed record.">Source provenance</span><h2>Trace this record to CDSCO</h2></div><span className="verified-label"><Icon name="check" size={15}/>{record.extractionStatus}</span></div>
    <div className="provenance-chain">
      <div><span>Parsed record</span><strong>Record {record.id}</strong></div><i>extracted from</i>
      <div><span>Extracted record</span><strong>{record.sourceLocation}</strong></div><i>published in</i>
      <div><span>Official document</span><strong>{record.source.shortTitle}</strong></div>
    </div>
    <dl className="definition-grid"><div><dt>Official source title</dt><dd>{record.source.title}</dd></div><div><dt>Source location</dt><dd>{record.sourceLocation}</dd></div><div><dt>Source snapshot SHA-256</dt><dd className="hash-value">{record.source.checksum}</dd></div><div><dt>Extraction status</dt><dd>{record.extractionStatus}</dd></div></dl>
    <div className="panel-actions"><SourceLink source={record.source}/><a className="subtle-link" href={record.source.indexUrl} target="_blank" rel="noreferrer">View CDSCO alerts index</a></div>
  </section>
}
