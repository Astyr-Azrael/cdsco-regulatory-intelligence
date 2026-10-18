import React, { useEffect, useState } from 'react'
import { Icon } from '../components/Icons.jsx'
import { RecordTable } from '../components/RecordTable.jsx'
import { DataState } from '../components/DataState.jsx'
import { api } from '../api.js'
import { useRemote } from '../hooks/useRemote.js'

export function SearchPage({ navigate, initialQuery = '' }) {
  const [query, setQuery] = useState(initialQuery)
  const [committed, setCommitted] = useState(initialQuery)
  const [year, setYear] = useState('')
  const [eventType, setEventType] = useState('')
  const [source, setSource] = useState('')
  const [authority, setAuthority] = useState('')
  useEffect(() => { const timer = setTimeout(() => setCommitted(query.trim()), 250); return () => clearTimeout(timer) }, [query])
  const key = JSON.stringify({ committed, year, eventType, source, authority })
  const state = useRemote(key, async () => {
    if (!committed) return { items: [], total: 0, entities: { manufacturers: [], drugs: [] } }
    const filters = { year, event_type: eventType, source, authority, page_size: 100 }
    const [records, entities] = await Promise.all([api.search({ q: committed, ...filters }), api.entitySearch(committed)])
    api.track({ event_type: records.total ? 'SEARCH_PERFORMED' : 'ZERO_RESULT', query: committed, filters })
    if (year || eventType || source || authority) api.track({ event_type: 'FILTER_USED', query: committed, filters })
    return { ...records, entities }
  })
  const sourceState = useRemote('search-sources', api.sources)
  return <>
    <header className="page-heading"><span className="page-eyebrow">Corpus search</span><h1>Search regulatory records</h1><p>Search products, manufacturer mentions, batches, findings, laboratories and official document titles.</p></header>
    <div className="search-page-box"><Icon name="search"/><input autoFocus value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search product, manufacturer, batch or finding" aria-label="Search records"/></div>
    <div className="filter-bar search-filters"><label>Year<select value={year} onChange={(event) => setYear(event.target.value)}><option value="">All years</option>{[...new Set((sourceState.data?.items || []).map(s => s.publication_date?.slice(0,4)).filter(Boolean))].sort().map(y => <option key={y} value={y}>{y}</option>)}</select></label><label>Event type<select value={eventType} onChange={(event) => setEventType(event.target.value)}><option value="">All events</option><option value="NSQ">CDSCO NSQ</option><option value="STATE_NSQ">State NSQ</option><option value="SPURIOUS">Spurious</option><option value="REVISED_ALERT">Revised alert</option></select></label><label>Source<select value={source} onChange={(event) => setSource(event.target.value)}><option value="">All documents</option>{sourceState.data?.items.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}</select></label><label>Reporting authority<input value={authority} onChange={(event) => setAuthority(event.target.value)} placeholder="Laboratory or authority"/></label></div>
    {committed ? <DataState loading={state.loading} error={state.error} empty={!state.data?.total && !state.data?.entities?.manufacturers.length && !state.data?.entities?.drugs.length}>{state.data && <><div className="results-summary"><strong>{state.data.total} matching records</strong><span>for “{committed}”</span></div>{(state.data.entities.manufacturers.length > 0 || state.data.entities.drugs.length > 0) && <section className="entity-search-results"><div><span className="section-kicker">Canonical entities</span><h2>Entity clusters</h2></div><div className="entity-result-grid">{state.data.entities.manufacturers.map((entity) => <button key={`m-${entity.id}`} onClick={() => navigate(`/manufacturers/${entity.id}`)}><small>Manufacturer</small><strong>{entity.name}</strong><span>{entity.record_count} linked records</span></button>)}{state.data.entities.drugs.map((entity) => <button key={`d-${entity.id}`} onClick={() => navigate(`/drugs/${entity.id}`)}><small>Drug / product</small><strong>{entity.name}</strong><span>{entity.record_count} linked records</span></button>)}</div></section>}<RecordTable records={state.data.items} navigate={navigate}/></>}</DataState> : <div className="search-guidance"><h2>Search fields</h2><div><span>Canonical drug or product</span><span>Canonical manufacturer</span><span>Source aliases</span><span>Batch or lot number</span><span>Regulatory finding</span><span>Laboratory or authority</span></div><p>Entity clusters show their aliases and linked regulatory history. Uncertain fuzzy candidates remain outside canonical profiles until review.</p></div>}
  </>
}
