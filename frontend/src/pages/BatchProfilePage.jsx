import React from 'react'
import { ProvenancePanel } from '../components/ProvenancePanel.jsx'
import { records } from '../data/records.js'

export function BatchProfilePage({ batch, navigate }) {
  const record = records.find((r) => r.batch === batch) || records[0]
  return <>
    <header className="entity-header"><div><span className="entity-type">Batch / lot entity</span><h1>{record.batch}</h1><p>{record.drug.name}</p></div><span className="record-status">Listed in an official NSQ alert</span></header>
    <div className="profile-grid"><section className="info-panel"><span className="section-kicker">Batch identity</span><h2>Product and manufacture</h2><dl className="definition-grid"><div><dt>Batch number</dt><dd>{record.batch}</dd></div><div><dt>Manufacturing date</dt><dd>{record.manufactured}</dd></div><div><dt>Expiry date</dt><dd>{record.expiry}</dd></div><div><dt>Manufacturer</dt><dd><button className="inline-link" onClick={() => navigate(`/manufacturers/${record.manufacturerId}`)}>{record.manufacturer.name}</button></dd></div></dl></section><section className="info-panel"><span className="section-kicker">Regulatory event</span><h2>Recorded finding</h2><dl className="definition-grid"><div><dt>Event type</dt><dd>{record.type}</dd></div><div><dt>Result stated in source</dt><dd>{record.reason}</dd></div><div><dt>Reporting laboratory</dt><dd>{record.laboratory}</dd></div><div><dt>Publication date</dt><dd>{record.publicationDate}</dd></div></dl><button className="secondary-button" onClick={() => navigate(`/events/${record.id}`)}>Open full event record</button></section></div>
    <div className="interpretation-box"><strong>Record-level interpretation</strong><p>This alert concerns the cited sample and batch. It does not establish a safety conclusion about every batch of the product or every product made by the manufacturer.</p></div>
    <ProvenancePanel record={record}/>
  </>
}
