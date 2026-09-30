import React from 'react'
import { StatusBadge } from '../components/StatusBadge.jsx'
import { ProvenancePanel } from '../components/ProvenancePanel.jsx'
import { getEvent, records } from '../data/records.js'

export function EventDetailPage({ id, navigate }) {
  const event = getEvent(id)
  const record = records.find((r) => r.id === event?.id) || records[0]
  return <>
    <header className="event-header"><div><span className="entity-type">Regulatory event record</span><h1>{record.source.shortTitle}</h1><p>Structured event {record.id} · source row {record.sourceRow}</p></div><StatusBadge>{record.type}</StatusBadge></header>
    <section className="record-sheet"><div className="record-sheet-title"><h2>Extracted regulatory fields</h2><span>{record.extractionStatus}</span></div><dl className="record-fields"><div><dt>Drug / product</dt><dd><button onClick={() => navigate(`/drugs/${record.productId}`)}>{record.drug.name}</button></dd><small>Raw value retained from source row</small></div><div><dt>Batch number</dt><dd><button onClick={() => navigate(`/batches/${record.batch}`)}>{record.batch}</button></dd><small>Normalized without changing source value</small></div><div><dt>Manufacturer</dt><dd><button onClick={() => navigate(`/manufacturers/${record.manufacturerId}`)}>{record.manufacturer.name}</button></dd><small>Canonical entity linked from “{record.manufacturer.rawName}”</small></div><div><dt>Manufacturing / expiry</dt><dd>{record.manufactured} · {record.expiry}</dd><small>Dates transcribed from source table</small></div><div><dt>NSQ result</dt><dd>{record.reason}</dd><small>Regulator-published wording normalized for case only</small></div><div><dt>Reported by</dt><dd>{record.laboratory}</dd><small>Laboratory named in source document</small></div></dl></section>
    <ProvenancePanel record={record}/>
  </>
}
