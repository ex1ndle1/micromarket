import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'

export default function Register() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [cardNumber, setCardNumber] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await api.registerUser({ username, card_number: parseInt(cardNumber, 10) })
      navigate('/products')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <h1>Enlist</h1>

      <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
        New blood. New opportunities. Join the network.
      </p>

      <form onSubmit={handleSubmit} className="form">
        <label className="field">
          <span>Code Name</span>
          <input
            type="text"
            placeholder='e.g. "El Patron"'
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="input"
            required
            minLength={2}
          />
        </label>

        <label className="field">
          <span>Account Number</span>
          <input
            type="text"
            inputMode="numeric"
            pattern="[0-9]{16}"
            maxLength={16}
            placeholder="0000000000000000"
            value={cardNumber}
            onChange={(e) => setCardNumber(e.target.value)}
            className="input"
            required
          />
        </label>

        {error && <div className="error">{error}</div>}

        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Processing...' : 'Join'}
        </button>
      </form>
    </div>
  )
}
