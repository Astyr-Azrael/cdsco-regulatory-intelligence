import React from 'react'
import { StatusBadge } from './StatusBadge.jsx'
import { SourceLink } from './SourceLink.jsx'

export function RecordTable({ records, navigate, compact = false }) {
  return <div className="table-wrap">
    <table className="records-table">
      <thead><tr><th>Alert</th><th>Product / batch</th><th>Manufacturer</th><th>NSQ result</th>{!compact && <th>Source</th>}</tr></thead>
      <tbody>{records.map((record) => <tr key={record.id}>
        <td><StatusBadge>{record.type}</StatusBadge><span className="cell-meta">{record.publicationDate}</span></td>
        <td><button className="table-link" onClick={() => navigate(`/drugs/${record.productId}`)}>{record.drug.name}</button><button className="batch-link" onClick={() => navigate(`/batches/${record.batch}`)}>Batch {record.batch}</button></td>
        <td><button className="table-link secondary" onClick={() => navigate(`/manufacturers/${record.manufacturerId}`)}>{record.manufacturer.name}</button></td>
        <td>{record.reason}<span className="cell-meta">Reported by {record.laboratory}</span></td>
        {!compact && <td><SourceLink source={record.source} label={`Page ${record.sourcePage}, row ${record.sourceRow}`}/></td>}
      </tr>)}</tbody>
    </table>
  </div>
}
