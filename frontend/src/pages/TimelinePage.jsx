import React from 'react'
import { Timeline } from '../components/Timeline.jsx'
import { DataState } from '../components/DataState.jsx'
import { api } from '../api.js'
import { useRemote } from '../hooks/useRemote.js'

export function TimelinePage({ navigate }) {
  const state = useRemote('timeline', async () => {
    const first = await api.search({ page: 1, page_size: 100 })
    const pageCount = Math.ceil(first.total / 100)
    const remaining = pageCount > 1 ? await Promise.all(Array.from({ length: pageCount - 1 }, (_, index) => api.search({ page: index + 2, page_size: 100 }))) : []
    return { items: [first, ...remaining].flatMap((page) => page.items), total: first.total }
  })
  return <>
    <header className="page-heading"><span className="page-eyebrow">Regulatory chronology</span><h1>Regulatory-history timeline</h1><p>Review the indexed regulatory records in publication order while retaining product, manufacturer, batch and official-source evidence.</p></header>
    <DataState loading={state.loading} error={state.error} empty={!state.data?.total}>{state.data && <><div className="filter-bar"><div className="filter-count">{state.data.total} source-backed records</div></div><Timeline records={state.data.items} navigate={navigate}/></>}</DataState>
  </>
}
