import { useState, useEffect } from 'react'
import { api } from '../api/client'

export default function Products() {
  const [id, setId] = useState('')
  const [product, setProduct] = useState(null)
  const [products, setProducts] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.listProducts()
      .then(setProducts)
      .catch(() => {})
  }, [])

  async function handleSearch(e) {
    e.preventDefault()
    if (!id) return
    setLoading(true)
    setError('')
    setProduct(null)
    try {
      const data = await api.getProduct(id)
      setProduct(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <h1>Inventory</h1>

      <form onSubmit={handleSearch} className="search-form">
        <input
          type="number"
          placeholder="Product ID"
          value={id}
          onChange={(e) => setId(e.target.value)}
          className="input"
        />
        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {product && (
        <div className="card">
          <h2>Product #{product.id}</h2>
          <p><span className="badge">{product.title}</span></p>
          <p><strong>Price:</strong> ${product.price}</p>
        </div>
      )}

      <h2 style={{ marginTop: '2rem', color: 'var(--primary)' }}>All Stock</h2>

      <div className="card-grid">
        {products.length === 0 && <p style={{ color: 'var(--text-muted)' }}>Nothing yet. Add some supply.</p>}
        {products.map((p) => (
          <div className="card" key={p.id}>
            <h2>{p.title}</h2>
            <p><span className="badge">ID: {p.id}</span></p>
            <p><strong>Price:</strong> ${p.price}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
