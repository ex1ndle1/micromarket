import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'

export default function CreateProduct() {
  const navigate = useNavigate()
  const [title, setTitle] = useState('')
  const [price, setPrice] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await api.createProduct({ title, price: parseFloat(price) })
      navigate('/products')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <h1>New Supply</h1>

      <form onSubmit={handleSubmit} className="form">
        <label className="field">
          <span>Product Name</span>
          <input
            type="text"
            placeholder='e.g. "Colombian Gold"'
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="input"
            required
            minLength={1}
          />
        </label>

        <label className="field">
          <span>Price (USD)</span>
          <input
            type="number"
            step="0.01"
            min="0.01"
            placeholder="99.99"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            className="input"
            required
          />
        </label>

        {error && <div className="error">{error}</div>}

        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Processing...' : 'Submit Shipment'}
        </button>
      </form>
    </div>
  )
}
