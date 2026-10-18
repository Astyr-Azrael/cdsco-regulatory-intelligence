import React from 'react'
import { RecordTable } from '../components/RecordTable.jsx'
import { Timeline } from '../components/Timeline.jsx'
import { DataState } from '../components/DataState.jsx'
import { api } from '../api.js'
import { useRemote } from '../hooks/useRemote.js'

export function BatchProfilePage({ batch, navigate }) {
  const state = useRemote(batch, () => api.batch(batch))
  return <DataState loading={state.loading} error={state.error} empty={!state.data?.total}>{state.data && <>
    <header className="entity-header"><div><span className="entity-type">Batch occurrences</span><h1>{batch}</h1><p>{state.data.total} source records across {state.data.contexts.length} product and manufacturer contexts.</p></div></header>
    <p className="method-note">{state.data.ambiguous ? 'This batch wording occurs in different product or manufacturer contexts. Each context has its own records below.' : 'Records are grouped by product, manufacturer and observed site address. This grouping does not establish a globally unique batch identity.'}</p>
    {state.data.contexts.map((context, index) => <section className="content-section" key={index}>
      <h2>{context.product}</h2><p>{context.manufacturer}</p>
      <RecordTable records={context.items} navigate={navigate}/>
      <h3>Recorded history in this context</h3><Timeline records={context.items} navigate={navigate}/>
    </section>)}
  </>}</DataState>
}
