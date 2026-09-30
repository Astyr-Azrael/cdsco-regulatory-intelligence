import React from 'react'

export function StatusBadge({ children, tone = 'red' }) {
  return <span className={`status-badge status-${tone}`}>{children}</span>
}
