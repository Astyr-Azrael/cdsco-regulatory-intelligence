import React from 'react'
import { StatusBadge } from '../components/StatusBadge.jsx'
import { ProvenancePanel } from '../components/ProvenancePanel.jsx'
import { DataState } from '../components/DataState.jsx'
import { api } from '../api.js'
import { useRemote } from '../hooks/useRemote.js'

export function EventDetailPage({ id, navigate }) {
  const state = useRemote(id, async () => { const result = await api.event(id); api.track({ event_type: 'RECORD_VIEWED', entity_type: 'REGULATORY_RECORD', entity_id: String(id) }); return result })
  const record = state.data
  return <DataState loading={state.loading} error={state.error} empty={!record}>{record && <>
    <header className="event-header"><div><span className="entity-type">Regulatory event record</span><h1>{record.source.shortTitle}</h1><p>Structured event {record.id} · source row {record.sourceRow}</p></div><StatusBadge>{record.type}</StatusBadge></header>
    <section className="record-sheet"><div className="record-sheet-title"><h2>Extracted regulatory fields</h2><span>{record.extractionStatus}</span></div><dl className="record-fields"><div><dt>Drug / product</dt><dd><button onClick={() => navigate(`/drugs/${record.productId}`)}>{record.canonicalDrug?.name || record.drug.name}</button></dd><small>Source mention: {record.drug.name}</small></div><div><dt>Batch number</dt><dd><button onClick={() => navigate(`/batches/${encodeURIComponent(record.batch)}`)}>{record.batch}</button></dd><small>Raw batch value retained</small></div><div><dt>Manufacturer</dt><dd><button disabled={!record.canonicalManufacturer} onClick={() => navigate(`/manufacturers/${record.manufacturerId}`)}>{record.canonicalManufacturer?.name || record.manufacturer.name}</button></dd><small>Source mention: {record.manufacturer.name}</small></div><div><dt>Manufacturing / expiry</dt><dd>{record.manufactured} · {record.expiry}</dd><small>Raw dates retained from source table</small></div><div><dt>Regulatory finding</dt><dd>{record.reason}</dd><small>Regulator-published wording with whitespace normalization only</small></div><div><dt>Reported by</dt><dd>{record.laboratory}</dd><small>Laboratory or authority named in the source</small></div></dl></section>
    {(record.canonicalDrug || record.canonicalManufacturer) && <section className="resolution-summary"><span className="section-kicker">Entity resolution</span><h2>Linked canonical identities</h2><p>Deterministic normalization linked these source mentions. Raw CDSCO wording remains above and in provenance.</p><div>{record.canonicalDrug && <span>Drug: {record.canonicalDrug.name} · {record.canonicalDrug.match_method.replaceAll('_', ' ')}</span>}{record.canonicalManufacturer && <span>Manufacturer: {record.canonicalManufacturer.name} · {record.canonicalManufacturer.match_method.replaceAll('_', ' ')}</span>}</div></section>}
    <ProvenancePanel record={record}/>
  </>}</DataState>
}
