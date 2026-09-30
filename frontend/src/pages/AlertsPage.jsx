import React, { useMemo, useState } from 'react'
import { RecordTable } from '../components/RecordTable.jsx'
import { records } from '../data/records.js'

export function AlertsPage({ navigate }) {
  const [month, setMonth] = useState('All months')
  const [reason, setReason] = useState('All results')
  const filtered = useMemo(() => records.filter((r) => (month === 'All months' || r.eventMonth === month) && (reason === 'All results' || r.reason.toLowerCase().includes(reason.toLowerCase()))), [month, reason])
  return <>
    <header className="page-heading"><span className="page-eyebrow">Regulatory records</span><h1>CDSCO alert index</h1><p>Structured records extracted from official CDSCO monthly NSQ documents. Filters apply to the indexed research sample.</p></header>
    <div className="filter-bar"><label>Alert month<select value={month} onChange={(e) => setMonth(e.target.value)}><option>All months</option><option>March 2025</option><option>April 2025</option><option>May 2025</option></select></label><label>Recorded result<select value={reason} onChange={(e) => setReason(e.target.value)}><option>All results</option><option>Dissolution</option><option>Assay</option><option>Sterility</option><option>Particulate matter</option></select></label><div className="filter-count">{filtered.length} matching records</div></div>
    <RecordTable records={filtered} navigate={navigate}/>
  </>
}
