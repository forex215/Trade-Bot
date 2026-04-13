import { useEffect, useMemo, useState } from 'react'
import PriceChart from './components/PriceChart'
import SignalCard from './components/SignalCard'
import TradeControls from './components/TradeControls'
import TradeHistory from './components/TradeHistory'
import { closeTrade, fetchHistory, fetchPrice, fetchSignal, openTrade } from './api'

export default function App() {
  const [price, setPrice] = useState(null)
  const [signal, setSignal] = useState(null)
  const [history, setHistory] = useState([])
  const [priceSeries, setPriceSeries] = useState([])
  const [error, setError] = useState('')

  const activeTrade = useMemo(() => history.find((t) => t.status === 'OPEN'), [history])
  const progress = activeTrade ? Math.min(100, Math.max(0, (activeTrade.pnl_usd / 10) * 100)) : 0

  const refresh = async () => {
    try {
      const [p, s, h] = await Promise.all([fetchPrice(), fetchSignal(), fetchHistory()])
      setPrice(p)
      setSignal(s)
      setHistory(h.trades || [])
      setPriceSeries((prev) => [...prev.slice(-59), p.price])
      setError('')
    } catch {
      setError('Unable to fetch data from backend')
    }
  }

  useEffect(() => {
    refresh()
    const timer = setInterval(refresh, 2000)
    return () => clearInterval(timer)
  }, [])

  const onOpen = async (payload) => {
    try {
      await openTrade({
        ...payload,
        quantity: Number(payload.quantity),
        lot_size: Number(payload.lot_size),
        target_profit_usd: Number(payload.target_profit_usd),
      })
      refresh()
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to open trade')
    }
  }

  const onClose = async (id) => {
    try {
      await closeTrade(id)
      refresh()
    } catch {
      setError('Failed to close trade')
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 p-6 text-slate-100">
      <h1 className="mb-4 text-2xl font-bold">XAUUSD AI Scalping Dashboard</h1>
      {error && <p className="mb-3 rounded bg-rose-900/50 p-2 text-sm">{error}</p>}

      <div className="mb-4 grid gap-4 lg:grid-cols-3">
        <SignalCard signal={signal} />
        <div className="rounded-xl bg-slate-900 p-4 shadow-lg">
          <h2 className="text-sm text-slate-400">Live Price / Spread</h2>
          <p className="mt-2 text-3xl font-bold">{price?.price?.toFixed(2) || '--'}</p>
          <p className="text-sm text-slate-300">Bid: {price?.bid?.toFixed(2)} | Ask: {price?.ask?.toFixed(2)}</p>
          <p className="text-sm text-slate-300">Spread: {price?.spread?.toFixed(2)}</p>
          <p className="mt-2 text-sm">Trade status: <span className={activeTrade ? 'text-emerald-400' : 'text-slate-400'}>{activeTrade ? 'OPEN' : 'CLOSED'}</span></p>
          {activeTrade && (
            <>
              <p className="text-sm">PnL: <span className={activeTrade.pnl_usd >= 0 ? 'text-emerald-400' : 'text-rose-400'}>${activeTrade.pnl_usd.toFixed(2)}</span></p>
              <div className="mt-2 h-2 w-full rounded bg-slate-700">
                <div className="h-2 rounded bg-cyan-400" style={{ width: `${progress}%` }} />
              </div>
              <p className="mt-1 text-xs text-slate-400">Target progress ($10): {progress.toFixed(1)}%</p>
            </>
          )}
        </div>
        <TradeControls onOpen={onOpen} onClose={onClose} activeTrade={activeTrade} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <PriceChart points={priceSeries} />
        <TradeHistory trades={history} activeTradeId={activeTrade?.trade_id} />
      </div>
    </div>
  )
}
