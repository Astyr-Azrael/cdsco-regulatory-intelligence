import React from 'react'
import { Icon } from './Icons.jsx'

export function SourceLink({ source, label = 'Open official source PDF' }) {
  return <a className="source-link" href={source.url} target="_blank" rel="noreferrer"><Icon name="external" size={15}/>{label}</a>
}
