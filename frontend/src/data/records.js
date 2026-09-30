export const sources = [
  {
    id: 'SRC-APR-2025',
    title: 'Not of Standard Quality (NSQ) Alert for the Month of April 2025 — CDSCO/Central Laboratories',
    shortTitle: 'CDSCO NSQ Alert · April 2025',
    releaseDate: '20 May 2025',
    publishedMonth: 'April 2025',
    pages: 7,
    type: 'NSQ',
    url: 'https://www.cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadAlertsFiles/CDSCO%20NSQ%20ALERT%20FOR%20THE%20MONTH%20OF%20APRIL-2025.pdf',
    indexUrl: 'https://www.cdsco.gov.in/opencms/opencms/en/Notifications/Alerts/',
    retrievalDate: '30 September 2026',
    checksum: 'Demo index · verify against downloaded source',
  },
  {
    id: 'SRC-MAY-2025',
    title: 'Not of Standard Quality (NSQ) Alert for the Month of May 2025 — CDSCO/Central Laboratories',
    shortTitle: 'CDSCO NSQ Alert · May 2025',
    releaseDate: '20 June 2025',
    publishedMonth: 'May 2025',
    pages: 7,
    type: 'NSQ',
    url: 'https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadAlertsFiles/NSQ%20ALERT%20MAY-2025.pdf',
    indexUrl: 'https://www.cdsco.gov.in/opencms/opencms/en/Notifications/Alerts/',
    retrievalDate: '30 September 2026',
    checksum: 'Demo index · verify against downloaded source',
  },
  {
    id: 'SRC-MAR-2025',
    title: 'Not of Standard Quality (NSQ) Alert for the Month of March 2025 — CDSCO/Central Laboratories',
    shortTitle: 'CDSCO NSQ Alert · March 2025',
    releaseDate: '18 April 2025',
    publishedMonth: 'March 2025',
    pages: 9,
    type: 'NSQ',
    url: 'https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadAlertsFiles/NSQ%20Alert%20For%20The%20Month%20of%20March-2025.pdf',
    indexUrl: 'https://www.cdsco.gov.in/opencms/opencms/en/Notifications/Alerts/',
    retrievalDate: '30 September 2026',
    checksum: 'Demo index · verify against downloaded source',
  },
]

export const manufacturers = [
  {
    id: 'mfg-martin-brown', name: 'Martin & Brown Biosciences Private Limited',
    rawName: 'M/s. Martin & Brown Bio-sciences Pvt. Ltd.', aliases: ['Martin & Brown Bio-sciences Pvt. Ltd.'],
    address: 'K. No. 918/419, Malkumajra, Nalagarh Road, Baddi, Dist. Solan, Himachal Pradesh 173205',
    resolution: { score: 0.97, method: 'Deterministic legal-suffix normalization + address agreement', review: 'Auto-linked' },
  },
  {
    id: 'mfg-themis', name: 'Themis Medicare Limited', rawName: 'M/s. Themis Medicare Limited', aliases: ['Themis Medicare Ltd.'],
    address: 'Sector 6A, Plot No. 16, 17 & 18, IIE, SIDCUL, Haridwar, Uttarakhand 249403',
    resolution: { score: 0.96, method: 'Legal-suffix normalization + exact location tokens', review: 'Auto-linked' },
  },
  {
    id: 'mfg-mancare', name: 'Mancare Laboratories Private Limited', rawName: 'M/s. Mancare Laboratories Pvt. Ltd.', aliases: ['Mancare Laboratories Pvt. Ltd.'],
    address: 'Plot No. 11, Pharmacity, Selaqui, Dehradun, Uttarakhand 248011',
    resolution: { score: 0.98, method: 'Deterministic legal-suffix normalization', review: 'Auto-linked' },
  },
  {
    id: 'mfg-gidsha', name: 'Gidsha Pharmaceuticals', rawName: 'M/s. Gidsha Pharmaceuticals', aliases: [],
    address: 'Plot No. 611–612, Mega GIDC, Kharedi, Dahod, Gujarat 389151',
    resolution: { score: 1, method: 'Exact normalized name + address', review: 'Exact match' },
  },
  {
    id: 'mfg-shangrila', name: 'Shangrila Industries Private Limited', rawName: 'M/s. Shangrila Industries (P) Ltd.', aliases: ['Shangrila Industries (P) Ltd.'],
    address: 'Pharma Division, Mining, Rangpo, East Sikkim 737132',
    resolution: { score: 0.94, method: 'Legal-suffix normalization + location agreement', review: 'Auto-linked' },
  },
]

export const drugs = [
  { id: 'drug-cmc-eye-drops', name: 'Carboxymethyl Cellulose Sodium Eye Drops IP', aliases: ['Carboxymethylcellulose Sodium Eye Drops IP'], form: 'Eye drops', strength: 'Not stated', manufacturerIds: ['mfg-martin-brown'] },
  { id: 'drug-bupicain', name: 'Bupivacaine Hydrochloride Injection IP', aliases: ['Bupicain 0.5%'], form: 'Injection', strength: '0.5%', manufacturerIds: ['mfg-themis'] },
  { id: 'drug-pantoprazole', name: 'Pantoprazole Gastro-Resistant Tablets IP', aliases: ['Pantoshang-40'], form: 'Tablet', strength: '40 mg', manufacturerIds: ['mfg-mancare', 'mfg-shangrila'] },
  { id: 'drug-calxia', name: 'Calcium Carbonate + Vitamin D3 Tablets IP', aliases: ['CALXIA-500', 'CALXIA 500'], form: 'Tablet', strength: '500 mg + 250 IU', manufacturerIds: ['mfg-gidsha'] },
]

export const events = [
  { id: 'evt-apr-01', type: 'NSQ', publicationDate: '20 May 2025', eventMonth: 'April 2025', productId: 'drug-cmc-eye-drops', manufacturerId: 'mfg-martin-brown', batch: 'MO24H27', manufactured: 'August 2024', expiry: 'July 2026', reason: 'pH, sterility and assay', laboratory: 'CDL, Kolkata', sourceId: 'SRC-APR-2025', sourcePage: 1, sourceRow: 1, sourceLines: '13–22', extractionStatus: 'Verified against source text' },
  { id: 'evt-apr-04', type: 'NSQ', publicationDate: '20 May 2025', eventMonth: 'April 2025', productId: 'drug-bupicain', manufacturerId: 'mfg-themis', batch: 'BPC24007', manufactured: 'December 2024', expiry: 'October 2026', reason: 'Particulate matter and description', laboratory: 'CDL, Kolkata', sourceId: 'SRC-APR-2025', sourcePage: 1, sourceRow: 4, sourceLines: '43–52', extractionStatus: 'Verified against source text' },
  { id: 'evt-apr-06', type: 'NSQ', publicationDate: '20 May 2025', eventMonth: 'April 2025', productId: 'drug-pantoprazole', manufacturerId: 'mfg-mancare', batch: 'MT240578', manufactured: 'August 2024', expiry: 'July 2026', reason: 'Dissolution in buffer stage', laboratory: 'CDL, Kolkata', sourceId: 'SRC-APR-2025', sourcePage: 1, sourceRow: 6, sourceLines: '64–72', extractionStatus: 'Verified against source text' },
  { id: 'evt-may-01', type: 'NSQ', publicationDate: '20 June 2025', eventMonth: 'May 2025', productId: 'drug-calxia', manufacturerId: 'mfg-gidsha', batch: 'GTL1317', manufactured: 'December 2024', expiry: 'November 2026', reason: 'Dissolution for calcium', laboratory: 'CDL, Kolkata', sourceId: 'SRC-MAY-2025', sourcePage: 1, sourceRow: 1, sourceLines: '11–20', extractionStatus: 'Verified against source text' },
  { id: 'evt-may-02', type: 'NSQ', publicationDate: '20 June 2025', eventMonth: 'May 2025', productId: 'drug-calxia', manufacturerId: 'mfg-gidsha', batch: 'GTL1295', manufactured: 'December 2024', expiry: 'November 2026', reason: 'Dissolution for calcium', laboratory: 'CDL, Kolkata', sourceId: 'SRC-MAY-2025', sourcePage: 1, sourceRow: 2, sourceLines: '21–30', extractionStatus: 'Verified against source text' },
  { id: 'evt-mar-02', type: 'NSQ', publicationDate: '18 April 2025', eventMonth: 'March 2025', productId: 'drug-pantoprazole', manufacturerId: 'mfg-shangrila', batch: 'SP240165', manufactured: 'June 2024', expiry: 'May 2026', reason: 'Dissolution (buffer stage)', laboratory: 'CDL, Kolkata', sourceId: 'SRC-MAR-2025', sourcePage: 1, sourceRow: 2, sourceLines: '22–29', extractionStatus: 'Verified against source text' },
]

export const getDrug = (id) => drugs.find((item) => item.id === id)
export const getManufacturer = (id) => manufacturers.find((item) => item.id === id)
export const getEvent = (id) => events.find((item) => item.id === id)
export const getSource = (id) => sources.find((item) => item.id === id)

export const records = events.map((event) => ({
  ...event,
  drug: getDrug(event.productId),
  manufacturer: getManufacturer(event.manufacturerId),
  source: getSource(event.sourceId),
}))
