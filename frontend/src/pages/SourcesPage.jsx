import React from 'react'
import { Icon } from '../components/Icons.jsx'
import { DataState } from '../components/DataState.jsx'
import { api } from '../api.js'
import { useRemote } from '../hooks/useRemote.js'

export function SourcesPage() {
  const state = useRemote('sources', api.sources)
  return <>
    <header className="page-heading"><span className="page-eyebrow">Provenance register</span><h1>Official source documents</h1><p>Every curated event in the portal is linked to the CDSCO alert index and the exact PDF from which it was extracted.</p></header>
    <DataState loading={state.loading} error={state.error} empty={!state.data?.total}>{state.data && <div className="source-cards">{state.data.items.map((source) => <article key={source.id}><div className="source-card-icon"><Icon name="file" size={22}/></div><div><span className="source-id">SOURCE {source.id} · {source.alert_type.replaceAll('_', ' ')}</span><h2>{source.title}</h2><dl><div><dt>Publication date</dt><dd>{source.publication_date || 'Not available'}</dd></div><div><dt>Source format</dt><dd>{source.page_count ? `${source.page_count} pages` : 'Structured public feed'}</dd></div><div><dt>Structured rows</dt><dd>{source.record_count}</dd></div><div><dt>Extraction status</dt><dd>{source.extraction_status}</dd></div></dl><div className="source-card-actions"><a href={source.document_url} target="_blank" rel="noreferrer"><Icon name="external" size={15}/>{source.page_count ? 'Open official PDF' : 'Open official portal'}</a><a href={source.source_url} target="_blank" rel="noreferrer">Official source page</a></div><small className="source-hash">SHA-256 {source.sha256}</small></div></article>)}</div>}</DataState>
  </>
}
