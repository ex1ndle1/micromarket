import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Products from './pages/Products'
import CreateProduct from './pages/CreateProduct'
import Register from './pages/Register'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/products" element={<Products />} />
        <Route path="/products/new" element={<CreateProduct />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </Layout>
  )
}
