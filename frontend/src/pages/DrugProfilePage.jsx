import React from 'react'
import { RecordTable } from '../components/RecordTable.jsx'
import { Timeline } from '../components/Timeline.jsx'
import { DataState } from '../components/DataState.jsx'
import { api } from '../api.js'
import { useRemote } from '../hooks/useRemote.js'

export function DrugProfilePage({ id, navigate }) {
  const state = useRemote(id, async () => { const result = await api.drugEntity(id); api.track({ event_type: 'ENTITY_VIEWED', entity_type: 'DRUG', entity_id: String(id) }); return result })
  return <DataState loading={state.loading} error={state.error} empty={!state.data?.record_count}>{state.data && <>
    <header className="entity-header"><div><span className="entity-type">Canonical drug / product entity</span><h1>{state.data.canonical_name}</h1><p>Product wording cluster with strength and dosage-form distinctions retained. It does not imply interchangeability.</p></div><div className="entity-stat"><strong>{state.data.record_count}</strong><span>Regulatory records</span></div></header>
    <div className="profile-grid"><section className="info-panel"><span className="section-kicker">Aliases and source mentions</span><h2>Observed product wording</h2><div className="alias-list">{state.data.source_mentions.map((name) => <span key={name}>{name}</span>)}</div><dl className="definition-grid"><div><dt>Strength signals</dt><dd>{state.data.strengths.join(', ') || 'Not stated'}</dd></div><div><dt>Dosage forms</dt><dd>{state.data.dosage_forms.join(', ') || 'Not stated'}</dd></div></dl></section><section className="info-panel"><span className="section-kicker">Relationships</span><h2>Manufacturers in linked records</h2><div className="relationship-list">{[...new Map(state.data.records.filter((item) => item.canonicalManufacturer).map((item) => [item.canonicalManufacturer.id, item.canonicalManufacturer])).values()].map((manufacturer) => <button key={manufacturer.id} onClick={() => navigate(`/manufacturers/${manufacturer.id}`)}><span>{manufacturer.name}</span><small>Open canonical entity</small></button>)}</div></section></div>
    {state.data.review_decisions?.length > 0 && <section className="content-section"><h2>Recorded source review decisions</h2>{state.data.review_decisions.map((decision,index) => <p key={index}><strong>{decision.decision.replaceAll("_"," ")}</strong> · {decision.reason} <small>Primary review: {decision.reviewer}. Independent human review not recorded.</small></p>)}</section>}
    <section className="content-section"><div className="section-heading-row"><div><span className="section-kicker">Structured records</span><h2>Associated batches and events</h2></div></div><RecordTable records={state.data.records} navigate={navigate}/></section>
    <section className="content-section"><div className="section-heading-row"><div><span className="section-kicker">Chronology</span><h2>Entity regulatory history</h2></div></div><Timeline records={state.data.records} navigate={navigate}/></section>
  </>}</DataState>
}
