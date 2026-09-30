import React from 'react'
import { Icon } from '../components/Icons.jsx'
import { records, sources } from '../data/records.js'

export function SourcesPage() {
  return <>
    <header className="page-heading"><span className="page-eyebrow">Provenance register</span><h1>Official source documents</h1><p>Every curated event in the portal is linked to the CDSCO alert index and the exact PDF from which it was extracted.</p></header>
    <div className="source-cards">{sources.map((source) => <article key={source.id}><div className="source-card-icon"><Icon name="file" size={22}/></div><div><span className="source-id">{source.id}</span><h2>{source.title}</h2><dl><div><dt>Release date</dt><dd>{source.releaseDate}</dd></div><div><dt>Document length</dt><dd>{source.pages} pages</dd></div><div><dt>Indexed sample rows</dt><dd>{records.filter((r) => r.sourceId === source.id).length}</dd></div><div><dt>Retrieved</dt><dd>{source.retrievalDate}</dd></div></dl><div className="source-card-actions"><a href={source.url} target="_blank" rel="noreferrer"><Icon name="external" size={15}/>Open official PDF</a><a href={source.indexUrl} target="_blank" rel="noreferrer">CDSCO alert index</a></div></div></article>)}</div>
  </>
}
