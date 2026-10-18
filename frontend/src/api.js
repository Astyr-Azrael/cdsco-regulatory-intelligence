const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'

async function request(path, params = {}, options = {}) {
  const url = new URL(`${API_BASE}${path}`, window.location.origin)
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') url.searchParams.set(key, value)
  })
  const response = await fetch(url, options)
  if (!response.ok) throw new Error(response.status === 404 ? 'Record not found' : 'The regulatory data service is unavailable')
  return response.json()
}

export function toUiRecord(item) {
  const provenance = item.provenance || {}
  const canonicalDrug = item.canonical_drug
  const canonicalManufacturer = item.canonical_manufacturer
  return {
    ...item,
    id: String(item.id), type: item.alert_type,
    publicationDate: (provenance.date_precision === 'month' ? provenance.publication_date?.slice(0, 7) : provenance.publication_date) || 'Date unavailable', eventMonth: provenance.date_precision === 'month' ? 'Reporting month' : 'Publication date',
    productId: canonicalDrug?.id || encodeURIComponent(item.drug_name || ''), manufacturerId: canonicalManufacturer?.id || encodeURIComponent(item.manufacturer || ''),
    batch: item.batch_number || 'Not stated', manufactured: item.manufacturing_date || 'Not stated', expiry: item.expiry_date || 'Not stated',
    reason: item.regulatory_finding || 'Not stated', laboratory: item.testing_laboratory || item.sample_authority || 'Not stated',
    drug: { name: item.drug_name || 'Product not stated' }, manufacturer: { name: item.manufacturer || 'Manufacturer not stated', rawName: item.manufacturer || 'Not stated' },
    sourcePage: provenance.page, sourceRow: provenance.row, extractionStatus: item.parse_status,
    sourceLocation: provenance.source_system === 'CDSCO_CURRENT_NSQ_PORTAL' ? `Official portal row position ${provenance.row}` : `Page ${provenance.page} · Row ${provenance.row}`,
    canonicalDrug, canonicalManufacturer,
    source: { id: provenance.source_document_id, system: provenance.source_system, title: provenance.title || 'Official CDSCO regulatory document', shortTitle: provenance.title || 'CDSCO regulatory document', url: provenance.document_url, indexUrl: provenance.source_url, releaseDate: provenance.publication_date, checksum: provenance.content_hash_sha256 },
  }
}

export const api = {
  search: async (params = {}) => { const result = await request('/search', params); return { ...result, items: result.items.map(toUiRecord) } },
  event: async (id) => toUiRecord(await request(`/events/${id}`)),
  batch: async (batch) => { const result = await request(`/batches/${encodeURIComponent(batch)}`); return { ...result, items: result.items.map(toUiRecord), contexts: result.contexts.map(c => ({ ...c, items: c.items.map(toUiRecord) })) } },
  drug: async (name) => { const result = await request(`/drugs/${encodeURIComponent(name)}`); return { ...result, items: result.items.map(toUiRecord) } },
  manufacturer: async (name) => { const result = await request(`/manufacturers/${encodeURIComponent(name)}`); return { ...result, items: result.items.map(toUiRecord) } },
  drugEntity: async (id) => { const result = await request(`/entities/drugs/${id}`); return { ...result, records: result.records.map(toUiRecord) } },
  manufacturerEntity: async (id) => { const result = await request(`/entities/manufacturers/${id}`); return { ...result, records: result.records.map(toUiRecord) } },
  entitySearch: (q) => request('/entities/search', { q }),
  analytics: () => request('/analytics/summary'),
  usageAnalytics: () => request('/usage/summary'),
  sources: () => request('/sources'),
  track: (payload) => {
    let session = sessionStorage.getItem('cdsco-session')
    if (!session) { session = crypto.randomUUID(); sessionStorage.setItem('cdsco-session', session) }
    return request('/usage/events', {}, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...payload, session_id: session }) }).catch(() => null)
  },
}
