import React, { useState } from 'react'
import { RecordTable } from '../components/RecordTable.jsx'
import { DataState } from '../components/DataState.jsx'
import { api } from '../api.js'
import { useRemote } from '../hooks/useRemote.js'

export function AlertsPage({ navigate }) {
  const [type, setType] = useState('')
  const [authority, setAuthority] = useState('')
  const [page, setPage] = useState(1)
  const state = useRemote(`${type}|${authority}|${page}`, () => api.search({ event_type: type, authority, page, page_size: 100 }))
  return <>
    <header className="page-heading"><span className="page-eyebrow">Regulatory records</span><h1>Indexed CDSCO records</h1><p>Structured rows reconstructed from the preserved official PDFs, with page, table-row and document-hash evidence.</p></header>
    <div className="filter-bar"><label>Event type<select value={type} onChange={(event) => { setType(event.target.value); setPage(1) }}><option value="">All event types</option><option value="NSQ">CDSCO NSQ</option><option value="STATE_NSQ">State NSQ</option><option value="SPURIOUS">Spurious</option><option value="REVISED_ALERT">Revised alert</option></select></label><label>Reporting authority<input value={authority} onChange={(event) => { setAuthority(event.target.value); setPage(1) }} placeholder="Filter laboratory or authority"/></label><div className="filter-count">{state.data?.total ?? '—'} matching records</div></div>
    <DataState loading={state.loading} error={state.error} empty={!state.data?.total}>{state.data && <><RecordTable records={state.data.items} navigate={navigate}/><div className="pagination"><span>Page {page} of {Math.ceil(state.data.total / 100)}</span><button disabled={page === 1} onClick={() => setPage(page - 1)}>Previous</button><button disabled={page >= Math.ceil(state.data.total / 100)} onClick={() => setPage(page + 1)}>Next</button></div></>}</DataState>
  </>
}
