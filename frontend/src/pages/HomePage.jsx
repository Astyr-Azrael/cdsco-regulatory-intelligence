import React, { useState } from 'react'
import { Icon } from '../components/Icons.jsx'
import { RecordTable } from '../components/RecordTable.jsx'
import { records, drugs, manufacturers, sources } from '../data/records.js'

export function HomePage({ navigate }) {
  const [query, setQuery] = useState('')
  const submit = (event) => { event.preventDefault(); navigate(`/search?q=${encodeURIComponent(query)}`) }
  return <>
    <header className="page-heading compact-heading"><span className="page-eyebrow">Academic regulatory intelligence portal</span><h1>Search CDSCO regulatory records</h1><p>Find regulator-published events by drug, manufacturer or batch, then trace every curated field back to the official document.</p></header>
    <form className="global-search" onSubmit={submit}>
      <Icon name="search" size={22}/><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search drug, manufacturer, batch or source document" aria-label="Global search"/><button type="submit">Search records</button>
    </form>
    <div className="scope-note"><strong>Research prototype:</strong> the current interface contains a verified six-record sample from three official CDSCO monthly alert documents. It does not yet represent the complete CDSCO corpus.</div>
    <section className="summary-strip" aria-label="Indexed sample summary">
      <div><strong>{records.length}</strong><span>Regulatory events</span></div><div><strong>{drugs.length}</strong><span>Canonical drugs</span></div><div><strong>{manufacturers.length}</strong><span>Manufacturers</span></div><div><strong>{sources.length}</strong><span>Official documents</span></div>
    </section>
    <section className="content-section"><div className="section-heading-row"><div><span className="section-kicker">Latest indexed records</span><h2>Regulatory alerts</h2></div><button className="secondary-button" onClick={() => navigate('/alerts')}>View all alerts</button></div><RecordTable records={records.slice(0, 5)} navigate={navigate}/></section>
  </>
}
