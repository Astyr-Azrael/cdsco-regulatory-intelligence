import React from 'react'
import { Icon } from './Icons.jsx'
import { api } from '../api.js'

export function SourceLink({ source, label }) {
  if (!source?.url) return <span className="source-unavailable">Official link unavailable</span>
  return <a className="source-link" href={source.url} target="_blank" rel="noreferrer" onClick={() => api.track({ event_type: 'SOURCE_CLICKED', entity_type: 'SOURCE_DOCUMENT', entity_id: String(source.id) })}><Icon name="external" size={15}/>{label || (source.system === 'CDSCO_CURRENT_NSQ_PORTAL' ? 'Open official portal' : 'Open official source PDF')}</a>
}
