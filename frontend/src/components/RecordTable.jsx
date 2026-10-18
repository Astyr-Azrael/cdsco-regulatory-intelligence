import React from 'react'
import { StatusBadge } from './StatusBadge.jsx'
import { SourceLink } from './SourceLink.jsx'

export function RecordTable({ records, navigate, compact = false }) {
  return <div className="table-wrap">
    <table className="records-table">
      <thead><tr><th>Event</th><th>Product / batch</th><th>Manufacturer</th><th>Regulatory finding</th>{!compact && <th>Official source</th>}</tr></thead>
      <tbody>{records.map((record) => <tr key={record.id}>
        <td><StatusBadge>{record.type}</StatusBadge><span className="cell-meta">{record.publicationDate}</span></td>
        <td><button className="table-link" onClick={() => navigate(`/events/${record.id}`)}>{record.drug.name}</button><button className="batch-link" onClick={() => navigate(`/batches/${encodeURIComponent(record.batch)}`)}>Batch {record.batch}</button></td>
        <td>{record.canonicalManufacturer ? <button className="table-link secondary" onClick={() => navigate(`/manufacturers/${record.manufacturerId}`)}>{record.manufacturer.name}</button> : <span>{record.manufacturer.name}</span>}</td>
        <td>{record.reason}<span className="cell-meta">Reported by {record.laboratory}</span></td>
        {!compact && <td><span className="source-title">{record.source.shortTitle}</span><SourceLink source={record.source} label={record.sourceLocation}/></td>}
      </tr>)}</tbody>
    </table>
  </div>
}
