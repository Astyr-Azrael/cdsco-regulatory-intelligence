import React, { useState } from 'react'
import { Icon } from '../components/Icons.jsx'
import { RecordTable } from '../components/RecordTable.jsx'
import { DataState } from '../components/DataState.jsx'
import { api } from '../api.js'
import { useRemote } from '../hooks/useRemote.js'

export function HomePage({ navigate }) {
  const [query, setQuery] = useState('')
  const state = useRemote('home', async () => {
    const [summary, records] = await Promise.all([api.analytics(), api.search({ page_size: 5 })])
    return { summary, records: records.items }
  })
  const submit = (event) => { event.preventDefault(); navigate(`/search?q=${encodeURIComponent(query)}`) }
  return <>
    <header className="page-heading compact-heading"><span className="page-eyebrow">Academic regulatory intelligence portal</span><h1>Search CDSCO regulatory records</h1><p>Find regulator-published events by drug, manufacturer or batch, then trace every curated field back to the official document.</p></header>
    <form className="global-search" onSubmit={submit}>
      <Icon name="search" size={22}/><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search drug, manufacturer, batch or source document" aria-label="Global search"/><button type="submit">Search records</button>
    </form>
    <DataState loading={state.loading} error={state.error}>
      {state.data && <>
        <div className="scope-note"><strong>Indexed regulatory corpus:</strong> {state.data.summary.coverage.start} — {state.data.summary.coverage.end} · last synchronized {state.data.summary.last_synchronized ? new Date(state.data.summary.last_synchronized).toLocaleString() : 'not available'}. Coverage is limited to the ingested sources shown in the register.</div>
        <section className="summary-strip" aria-label="Indexed corpus summary">
          <div><strong>{state.data.summary.regulatory_records}</strong><span>Regulatory records</span></div><div><strong>{state.data.summary.distinct_product_mentions}</strong><span>Product mentions</span></div><div><strong>{state.data.summary.distinct_manufacturer_mentions}</strong><span>Manufacturer mentions</span></div><div><strong>{state.data.summary.official_documents}</strong><span>Official documents</span></div>
        </section>
        <section className="content-section"><div className="section-heading-row"><div><span className="section-kicker">Latest indexed records</span><h2>Regulatory records</h2></div><button className="secondary-button" onClick={() => navigate('/alerts')}>View all records</button></div><RecordTable records={state.data.records} navigate={navigate}/></section>
      </>}
    </DataState>
  </>
}
