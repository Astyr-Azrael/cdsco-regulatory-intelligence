import React from 'react'

export function DataState({ loading, error, empty, children }) {
  if (loading) return <div className="data-state" role="status"><strong>Loading regulatory records…</strong><p>Retrieving the indexed corpus and source provenance.</p></div>
  if (error) return <div className="data-state error-state" role="alert"><strong>Data service unavailable</strong><p>{error.message}. Start the FastAPI service and try again.</p></div>
  if (empty) return <div className="data-state"><strong>No matching records</strong><p>The indexed corpus contains no records for the current query or filters.</p></div>
  return children
}
