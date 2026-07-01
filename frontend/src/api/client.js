const BASE = ''

async function request(method, path, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  }
  if (body) opts.body = JSON.stringify(body)
  const res = await fetch(`${BASE}${path}`, opts)
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(detail.detail || `Request failed (${res.status})`)
  }
  return res.json()
}

export const api = {
  getProduct: (id) => request('GET', `/market/product?id=${id}`),
  listProducts: () => request('GET', '/market/products'),
  createProduct: (data) => request('POST', '/market/product', data),
  registerUser: (data) => request('POST', '/user/register', data),
}
