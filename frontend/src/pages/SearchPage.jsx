import React, { useMemo, useState } from 'react'
import { Icon } from '../components/Icons.jsx'
import { records, drugs, manufacturers } from '../data/records.js'

export function SearchPage({ navigate, initialQuery = '' }) {
  const [query, setQuery] = useState(initialQuery)
  const q = query.trim().toLowerCase()
  const results = useMemo(() => {
    if (!q) return []
    const drugResults = drugs.filter((d) => [d.name, ...d.aliases].join(' ').toLowerCase().includes(q)).map((d) => ({ type: 'Drug', title: d.name, alias: d.aliases.join(' · ') || 'No indexed aliases', path: `/drugs/${d.id}`, events: records.filter((r) => r.productId === d.id).length }))
    const mfgResults = manufacturers.filter((m) => [m.name, m.rawName, ...m.aliases, m.address].join(' ').toLowerCase().includes(q)).map((m) => ({ type: 'Manufacturer', title: m.name, alias: `Matched source mention: ${m.rawName}`, path: `/manufacturers/${m.id}`, events: records.filter((r) => r.manufacturerId === m.id).length }))
    const batchResults = records.filter((r) => r.batch.toLowerCase().includes(q)).map((r) => ({ type: 'Batch', title: r.batch, alias: `${r.drug.name} · ${r.manufacturer.name}`, path: `/batches/${r.batch}`, events: 1 }))
    return [...drugResults, ...mfgResults, ...batchResults]
  }, [q])
  return <>
    <header className="page-heading"><span className="page-eyebrow">Entity discovery</span><h1>Search regulatory entities</h1><p>Search canonical names and original source mentions across the indexed sample.</p></header>
    <div className="search-page-box"><Icon name="search"/><input autoFocus value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Try Pantoprazole, Gidsha or MT240578" aria-label="Search records"/></div>
    {q ? <><div className="results-summary"><strong>{results.length} results</strong><span>for “{query}”</span></div><div className="search-results">{results.map((result) => <button key={`${result.type}-${result.title}`} onClick={() => navigate(result.path)}><span className="result-kind">{result.type}</span><span className="result-main"><strong>{result.title}</strong><small>{result.alias}</small></span><span className="result-events">{result.events} {result.events === 1 ? 'event' : 'events'}</span><Icon name="chevron"/></button>)}</div>{!results.length && <div className="empty-state"><h2>No indexed matches</h2><p>Try another entity name or batch number. The research sample is intentionally limited.</p></div>}</> : <div className="search-guidance"><h2>Search fields</h2><div><span>Drug or product</span><span>Manufacturer or source alias</span><span>Batch or lot number</span></div></div>}
  </>
}
