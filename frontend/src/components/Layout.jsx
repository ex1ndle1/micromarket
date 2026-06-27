import { Link, useLocation } from 'react-router-dom'

const links = [
  { to: '/products', label: 'Inventory' },
  { to: '/products/new', label: 'New Supply' },
  { to: '/register', label: 'Enlist' },
]

export default function Layout({ children }) {
  const { pathname } = useLocation()

  return (
    <div className="layout">
      <nav className="nav">
        <Link to="/" className="nav-logo">Narco Empire</Link>
        <div className="nav-links">
          {links.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              className={pathname === l.to ? 'nav-link active' : 'nav-link'}
            >
              {l.label}
            </Link>
          ))}
        </div>
      </nav>
      <main className="main">{children}</main>
    </div>
  )
}
