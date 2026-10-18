import React from 'react'

export function StatusBadge({ children, tone = 'red' }) {
  const descriptions = {
    NSQ: 'Not of Standard Quality — a tested sample that did not meet one or more applicable quality standards or specifications.',
    STATE_NSQ: 'A Not of Standard Quality record reported through a state source.',
    REVISED_ALERT: 'A later regulatory publication modifying or correcting previously published alert information.',
    SPURIOUS: 'A regulator-published spurious-drug record; see the official source for its exact status and remarks.',
  }
  return <span className={`status-badge status-${tone}`} title={descriptions[children] || ''}>{children}</span>
}
