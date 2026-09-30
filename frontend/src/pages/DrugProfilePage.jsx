import React from 'react'
import { RecordTable } from '../components/RecordTable.jsx'
import { Timeline } from '../components/Timeline.jsx'
import { getDrug, records, manufacturers } from '../data/records.js'

export function DrugProfilePage({ id, navigate }) {
  const drug = getDrug(id) || getDrug('drug-pantoprazole')
  const linked = records.filter((r) => r.productId === drug.id)
  const linkedManufacturers = manufacturers.filter((m) => drug.manufacturerIds.includes(m.id))
  return <>
    <header className="entity-header"><div><span className="entity-type">Canonical drug entity</span><h1>{drug.name}</h1><p>{drug.form} · {drug.strength}</p></div><div className="entity-stat"><strong>{linked.length}</strong><span>Linked regulatory events</span></div></header>
    <div className="profile-grid"><section className="info-panel"><span className="section-kicker">Identity</span><h2>Entity summary</h2><dl className="definition-grid"><div><dt>Canonical name</dt><dd>{drug.name}</dd></div><div><dt>Dosage form</dt><dd>{drug.form}</dd></div><div><dt>Strength</dt><dd>{drug.strength}</dd></div><div><dt>Known source aliases</dt><dd>{drug.aliases.join(', ')}</dd></div></dl></section><section className="info-panel"><span className="section-kicker">Relationships</span><h2>Associated manufacturers</h2><div className="relationship-list">{linkedManufacturers.map((m) => <button key={m.id} onClick={() => navigate(`/manufacturers/${m.id}`)}><span>{m.name}</span><small>{records.filter((r) => r.manufacturerId === m.id && r.productId === drug.id).length} linked record(s)</small></button>)}</div></section></div>
    <section className="content-section"><div className="section-heading-row"><div><span className="section-kicker">Structured records</span><h2>Associated batches and events</h2></div></div><RecordTable records={linked} navigate={navigate}/></section>
    <section className="content-section"><div className="section-heading-row"><div><span className="section-kicker">Chronology</span><h2>Regulatory history</h2></div></div><Timeline records={linked} navigate={navigate}/></section>
  </>
}
