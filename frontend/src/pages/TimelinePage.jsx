import React, { useState } from 'react'
import { Timeline } from '../components/Timeline.jsx'
import { records } from '../data/records.js'

export function TimelinePage({ navigate }) {
  const [entity, setEntity] = useState('All indexed entities')
  const filtered = entity === 'All indexed entities' ? records : records.filter((r) => r.drug.name === entity || r.manufacturer.name === entity)
  return <>
    <header className="page-heading"><span className="page-eyebrow">Temporal linking</span><h1>Regulatory-history timeline</h1><p>Review regulator-published events in chronological context while retaining the linked drug, manufacturer, batch and source.</p></header>
    <div className="filter-bar"><label>Entity<select value={entity} onChange={(e) => setEntity(e.target.value)}><option>All indexed entities</option><option>Pantoprazole Gastro-Resistant Tablets IP</option><option>Gidsha Pharmaceuticals</option></select></label><div className="filter-count">{filtered.length} linked events</div></div>
    <Timeline records={filtered} navigate={navigate}/>
  </>
}
