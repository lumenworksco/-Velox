import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Trading from './pages/Trading'
import Analytics from './pages/Analytics'
import Backtest from './pages/Backtest'
import Strategies from './pages/Strategies'
import Positions from './pages/Positions'
import Settings from './pages/Settings'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/trading" element={<Trading />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/backtest" element={<Backtest />} />
          <Route path="/strategies" element={<Strategies />} />
          <Route path="/positions" element={<Positions />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
