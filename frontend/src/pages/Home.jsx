import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function Home() {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    api.listProducts()
      .then((products) => setStats(products.length))
      .catch(() => {})
  }, [])

  return (
    <div className="page">
      <div className="hero">
        <h1>Empire Market</h1>
        <p className="tagline">Built Different.</p>
        <p>Global logistics & distribution network</p>
      </div>

      <div className="card-grid" style={{ marginTop: '2rem' }}>
        <div className="card">
          <h2>Inventory</h2>
          <p>Browse current supply ({stats ?? '?'} items)</p>
          <br />
          <Link to="/products" className="btn btn-secondary" style={{ textDecoration: 'none', display: 'inline-block' }}>
            View Stock
          </Link>
        </div>

        <div className="card">
          <h2>New Shipment</h2>
          <p>Register incoming product</p>
          <br />
          <Link to="/products/new" className="btn" style={{ textDecoration: 'none', display: 'inline-block' }}>
            Add Supply
          </Link>
        </div>

        <div className="card">
          <h2>Recruitment</h2>
          <p>New members welcome</p>
          <br />
          <Link to="/register" className="btn btn-secondary" style={{ textDecoration: 'none', display: 'inline-block' }}>
            Enlist Now
          </Link>
        </div>
      </div>
    </div>
  )
}
