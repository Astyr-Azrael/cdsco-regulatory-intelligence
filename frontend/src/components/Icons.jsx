import React from 'react'

const path = (d) => <path d={d} strokeLinecap="round" strokeLinejoin="round" />

export function Icon({ name, size = 19 }) {
  const paths = {
    home: path('M3 11.5 12 4l9 7.5V21H6V11.5M9 21v-6h6v6'),
    alert: path('M12 3 2.8 20h18.4L12 3Zm0 6v5m0 3h.01'),
    search: <><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></>,
    drug: <><path d="M7 4.5a4 4 0 0 1 5.7 0l6.8 6.8a4 4 0 0 1-5.7 5.7L7 10.2a4 4 0 0 1 0-5.7Z"/><path d="m10 13 5-5"/></>,
    building: path('M4 21V5l8-2v18m0-13h8v13M8 8h.01M8 12h.01M8 16h.01M16 12h.01M16 16h.01'),
    batch: path('M4 7h16M6 7v13h12V7M9 11h6M9 15h4M8 3h8v4'),
    file: path('M6 3h8l4 4v14H6V3Zm8 0v5h5M9 12h6M9 16h6'),
    timeline: path('M5 5v14m0-10h6m-6 6h10m-4-6 3-3m1 9 3-3'),
    chart: <><path d="M4 20V10h4v10M10 20V4h4v16M16 20v-7h4v7"/><path d="M2 20h20"/></>,
    source: path('M8 12h8m-6 4h4M7 3h10l4 4v14H3V7l4-4Zm10 0v5h5'),
    external: path('M14 4h6v6m0-6-9 9M19 14v6H4V5h6'),
    chevron: path('m9 18 6-6-6-6'),
    menu: path('M4 7h16M4 12h16M4 17h16'),
    close: path('m6 6 12 12M18 6 6 18'),
    link: path('M10 13a5 5 0 0 0 7.5.5l2-2a5 5 0 0 0-7-7l-1.1 1M14 11a5 5 0 0 0-7.5-.5l-2 2a5 5 0 0 0 7 7l1.1-1'),
    check: path('m5 12 4 4L19 6'),
  }
  return <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">{paths[name]}</svg>
}
