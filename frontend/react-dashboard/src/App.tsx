/**
 * Main App Component
 * 
 * Sets up routing and application structure
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { Territories } from './pages/Territories'
import { Clients } from './pages/Clients'
import { Advisors } from './pages/Advisors'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="territories" element={<Territories />} />
          <Route path="clients" element={<Clients />} />
          <Route path="advisors" element={<Advisors />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
