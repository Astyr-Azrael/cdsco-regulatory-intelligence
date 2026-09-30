import React from 'react'
import { Timeline } from '../components/Timeline.jsx'
import { getManufacturer, records } from '../data/records.js'

export function ManufacturerProfilePage({ id, navigate }) {
  const manufacturer = getManufacturer(id) || getManufacturer('mfg-gidsha')
  const linked = records.filter((r) => r.manufacturerId === manufacturer.id)
  return <>
    <header className="entity-header"><div><span className="entity-type">Canonical manufacturer entity</span><h1>{manufacturer.name}</h1><p>{manufacturer.address}</p></div><div className="entity-stat"><strong>{linked.length}</strong><span>Linked regulatory events</span></div></header>
    <div className="profile-grid"><section className="info-panel"><span className="section-kicker">Entity identity</span><h2>Canonical record</h2><dl className="definition-grid"><div><dt>Canonical name</dt><dd>{manufacturer.name}</dd></div><div><dt>Original source mention</dt><dd>{manufacturer.rawName}</dd></div><div><dt>Known aliases</dt><dd>{manufacturer.aliases.join(', ') || 'No additional aliases in sample'}</dd></div><div><dt>Unit / address</dt><dd>{manufacturer.address}</dd></div></dl></section><section className="resolution-panel"><span className="section-kicker">Entity resolution evidence</span><h2>Why these mentions were linked</h2><div className="score-row"><strong>{Math.round(manufacturer.resolution.score * 100)}%</strong><span>combined match confidence</span></div><div className="evidence-list"><div><b>Decision</b><span>{manufacturer.resolution.review}</span></div><div><b>Method</b><span>{manufacturer.resolution.method}</span></div><div><b>Human-verifiable evidence</b><span>Original mention and location are preserved beside the canonical entity.</span></div></div></section></div>
    <section className="content-section"><div className="section-heading-row"><div><span className="section-kicker">Related products</span><h2>Indexed product and batch relationships</h2></div></div><div className="relationship-table"><div className="relationship-head"><span>Product</span><span>Batch</span><span>Source record</span></div>{linked.map((r) => <button key={r.id} onClick={() => navigate(`/events/${r.id}`)}><span>{r.drug.name}</span><span>{r.batch}</span><span>{r.source.shortTitle}</span></button>)}</div></section>
    <section className="content-section"><div className="section-heading-row"><div><span className="section-kicker">Chronology</span><h2>Regulatory history</h2></div></div><Timeline records={linked} navigate={navigate}/></section>
  </>
}
