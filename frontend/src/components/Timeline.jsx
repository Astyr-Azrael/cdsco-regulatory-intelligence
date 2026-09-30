import React from 'react'
import { StatusBadge } from './StatusBadge.jsx'
import { SourceLink } from './SourceLink.jsx'

export function Timeline({ records, navigate }) {
  return <div className="timeline-list">
    {records.map((record) => <article className="timeline-item" key={record.id}>
      <div className="timeline-date"><strong>{record.publicationDate}</strong><span>{record.eventMonth} alert</span></div>
      <div className="timeline-marker"><span/></div>
      <div className="timeline-record">
        <div className="timeline-record-head"><StatusBadge>{record.type}</StatusBadge><button className="text-action" onClick={() => navigate(`/events/${record.id}`)}>View event record</button></div>
        <h3>{record.drug.name}</h3>
        <dl className="inline-fields"><div><dt>Batch</dt><dd>{record.batch}</dd></div><div><dt>Manufacturer</dt><dd>{record.manufacturer.name}</dd></div><div><dt>Recorded reason</dt><dd>{record.reason}</dd></div></dl>
        <div className="timeline-source"><span>{record.source.shortTitle} · Page {record.sourcePage}, row {record.sourceRow}</span><SourceLink source={record.source}/></div>
      </div>
    </article>)}
  </div>
}
