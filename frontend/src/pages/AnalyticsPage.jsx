import React from 'react'
import { records, sources } from '../data/records.js'

const Bar = ({ label, value, max, tone = '' }) => <div className="bar-row"><div className="bar-label"><span>{label}</span><strong>{value}</strong></div><div className="bar-track"><span className={tone} style={{ width: `${(value / max) * 100}%` }}/></div></div>

export function AnalyticsPage() {
  const monthCounts = ['March 2025', 'April 2025', 'May 2025'].map((m) => ({ label: m, value: records.filter((r) => r.eventMonth === m).length }))
  const reasonCounts = [{ label: 'Dissolution', value: records.filter((r) => r.reason.toLowerCase().includes('dissolution')).length }, { label: 'Sterility / assay', value: records.filter((r) => /sterility|assay/i.test(r.reason)).length }, { label: 'Particulate matter', value: records.filter((r) => /particulate/i.test(r.reason)).length }]
  return <>
    <header className="page-heading"><span className="page-eyebrow">Sample-level analytics</span><h1>Regulatory data dashboard</h1><p>Descriptive statistics for the indexed research sample. Event counts are not product or manufacturer safety rankings.</p></header>
    <div className="analytics-summary"><div><strong>{records.length}</strong><span>Structured events</span><small>Across the current sample</small></div><div><strong>{sources.length}</strong><span>Official source PDFs</span><small>March–May 2025</small></div><div><strong>100%</strong><span>Source-located</span><small>Page and row recorded</small></div><div><strong>5</strong><span>Manufacturers</span><small>Canonicalized entities</small></div></div>
    <div className="analytics-grid"><section className="chart-panel"><span className="section-kicker">Temporal distribution</span><h2>Indexed events by alert month</h2><div className="bar-chart">{monthCounts.map((item) => <Bar key={item.label} {...item} max={3}/>)}</div></section><section className="chart-panel"><span className="section-kicker">Recorded findings</span><h2>Failure-reason categories</h2><div className="bar-chart">{reasonCounts.map((item, i) => <Bar key={item.label} {...item} max={4} tone={i === 0 ? 'red-bar' : ''}/>)}</div></section><section className="chart-panel wide-chart"><span className="section-kicker">Document coverage</span><h2>Source document register</h2><div className="document-register">{sources.map((source) => <div key={source.id}><strong>{source.shortTitle}</strong><span>{source.pages} pages</span><span>{records.filter((r) => r.sourceId === source.id).length} extracted rows in sample</span><a href={source.url} target="_blank" rel="noreferrer">Official PDF</a></div>)}</div></section></div>
    <div className="method-note"><strong>Analytical limitation</strong><p>The charts describe the current six-record research sample. They must not be interpreted as prevalence estimates or as comparative judgments about medicines, manufacturers or locations.</p></div>
  </>
}
