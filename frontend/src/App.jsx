import React, { useEffect, useMemo, useState } from 'react'
import { Icon } from './components/Icons.jsx'
import { HomePage } from './pages/HomePage.jsx'
import { AlertsPage } from './pages/AlertsPage.jsx'
import { SearchPage } from './pages/SearchPage.jsx'
import { DrugProfilePage } from './pages/DrugProfilePage.jsx'
import { ManufacturerProfilePage } from './pages/ManufacturerProfilePage.jsx'
import { BatchProfilePage } from './pages/BatchProfilePage.jsx'
import { EventDetailPage } from './pages/EventDetailPage.jsx'
import { TimelinePage } from './pages/TimelinePage.jsx'
import { AnalyticsPage } from './pages/AnalyticsPage.jsx'
import { SourcesPage } from './pages/SourcesPage.jsx'

const navigation = [
  { section: 'Overview' },
  { path: '/home', label: 'Overview', icon: 'home' },
  { path: '/search', label: 'Search', icon: 'search' },
  { section: 'Regulatory records' },
  { path: '/alerts', label: 'Records', icon: 'alert' },
  { path: '/timeline', label: 'Timeline', icon: 'timeline' },
  { section: 'Entities' },
  { path: '/entities', label: 'Entity search', icon: 'search' },
  { section: 'Research' },
  { path: '/analytics', label: 'Analytics', icon: 'chart' },
  { path: '/sources', label: 'Sources', icon: 'source' },
]

function readRoute() {
  const hash = window.location.hash.replace(/^#/, '') || '/home'
  const [path, query = ''] = hash.split('?')
  return { path, params: new URLSearchParams(query) }
}

export default function App() {
  const [route, setRoute] = useState(readRoute)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  useEffect(() => {
    const update = () => { setRoute(readRoute()); setSidebarOpen(false); window.scrollTo(0, 0) }
    window.addEventListener('hashchange', update)
    if (!window.location.hash) window.location.hash = '/home'
    return () => window.removeEventListener('hashchange', update)
  }, [])
  const navigate = (path) => { window.location.hash = path }
  const active = (path) => route.path === path || (path.includes('/drugs/') && route.path.startsWith('/drugs/')) || (path.includes('/manufacturers/') && route.path.startsWith('/manufacturers/')) || (path.includes('/batches/') && route.path.startsWith('/batches/')) || (path.includes('/events/') && route.path.startsWith('/events/'))
  const content = useMemo(() => {
    const parts = route.path.split('/').filter(Boolean)
    if (route.path === '/home') return <HomePage navigate={navigate}/>
    if (route.path === '/alerts') return <AlertsPage navigate={navigate}/>
    if (route.path === '/search') return <SearchPage navigate={navigate} initialQuery={route.params.get('q') || ''}/>
    if (route.path === '/entities') return <SearchPage navigate={navigate} initialQuery={route.params.get('q') || ''}/>
    if (parts[0] === 'drugs') return <DrugProfilePage id={parts[1]} navigate={navigate}/>
    if (parts[0] === 'manufacturers') return <ManufacturerProfilePage id={parts[1]} navigate={navigate}/>
    if (parts[0] === 'batches') return <BatchProfilePage batch={decodeURIComponent(parts[1] || '')} navigate={navigate}/>
    if (parts[0] === 'events') return <EventDetailPage id={parts[1]} navigate={navigate}/>
    if (route.path === '/timeline') return <TimelinePage navigate={navigate}/>
    if (route.path === '/analytics') return <AnalyticsPage/>
    if (route.path === '/sources') return <SourcesPage/>
    return <HomePage navigate={navigate}/>
  }, [route])

  return <div className="app-shell">
    <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
      <div className="brand-block"><div className="brand-emblem"><Icon name="source" size={23}/></div><div><strong>CDSCO Regulatory<br/>Intelligence</strong><span>Academic research prototype</span></div></div>
      <nav aria-label="Primary navigation">{navigation.map((item, index) => item.section ? <span className="nav-section" key={`${item.section}-${index}`}>{item.section}</span> : <button key={item.path} className={active(item.path) ? 'active' : ''} onClick={() => navigate(item.path)}><Icon name={item.icon}/><span>{item.label}</span></button>)}</nav>
      <div className="sidebar-footer"><span>Data scope</span><strong>Indexed CDSCO corpus</strong><small>Coverage shown dynamically · not affiliated with CDSCO</small></div>
    </aside>
    {sidebarOpen && <button className="sidebar-scrim" aria-label="Close navigation" onClick={() => setSidebarOpen(false)}/>} 
    <div className="app-main">
      <header className="top-header"><button className="mobile-menu" onClick={() => setSidebarOpen(!sidebarOpen)} aria-label="Open navigation"><Icon name={sidebarOpen ? 'close' : 'menu'}/></button><div className="top-context"><span>Government source monitoring</span><strong>Provenance-aware research interface</strong></div><div className="header-meta"><span className="sample-pill">Indexed corpus</span><a href="https://www.cdsco.gov.in/opencms/opencms/en/Notifications/Alerts/" target="_blank" rel="noreferrer">Official CDSCO alerts <Icon name="external" size={14}/></a></div></header>
      <main className="page-content">{content}</main>
      <footer className="site-footer"><p>This academic prototype organizes regulator-published records. It does not provide medical advice, safety scores or independent regulatory judgments.</p><span>Source authority: Central Drugs Standard Control Organization</span></footer>
    </div>
  </div>
}
