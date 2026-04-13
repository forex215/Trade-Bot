import { useEffect, useMemo, useState } from 'react'
import PriceChart from './components/PriceChart'
import SignalCard from './components/SignalCard'
import TradeControls from './components/TradeControls'
import TradeHistory from './components/TradeHistory'
import { closeTrade, fetchHistory, fetchPrice, fetchSignal, getAutoTrade, openTrade, setAutoTrade, trainModel } from './api'

export default function App() {
  const [price, setPrice] = useState(null)
  const [signal, setSignal] = useState(null)
  const [history, setHistory] = useState([])
  const [priceSeries, setPriceSeries] = useState([])
  const [trainStats, setTrainStats] = useState(null)
  const [autoTrade, setAutoTradeState] = useState(false)
  const [wsStatus, setWsStatus] = useState('connecting')
  const [error, setError] = useState('')

  const activeTrade = useMemo(() => history.find((t) => t.status === 'OPEN'), [history])
  const target = Number(activeTrade?.take_profit ? Math.abs(activeTrade.take_profit - activeTrade.entry_price) * activeTrade.quantity : 10)
  const progress = activeTrade ? Math.min(100, Math.max(0, (activeTrade.pnl_usd / target) * 100)) : 0

  const refresh = async () => {
    try {
      const [p, s, h, auto] = await Promise.all([fetchPrice(), fetchSignal(), fetchHistory(), getAutoTrade()])
      setPrice(p)
      setSignal(s)
      setHistory(h.trades || [])
      setAutoTradeState(auto.enabled)
      setPriceSeries((prev) => [...prev.slice(-99), p.price])
      setError('')
    } catch {
      setError('Unable to fetch data from backend')
    }
  }

  useEffect(() => {
    refresh()
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/price'
    const ws = new WebSocket(wsUrl)
    ws.onopen = () => setWsStatus('live')
    ws.onclose = () => setWsStatus('offline')
    ws.onerror = () => setWsStatus('error')
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setPrice({ symbol: data.symbol, price: data.price, bid: data.bid, ask: data.ask, spread: data.spread })
      setSignal({
        signal: data.signal,
        confidence: data.confidence,
        win_probability: data.win_probability,
        lose_probability: data.lose_probability,
        reason: 'Realtime stream',
      })
      setAutoTradeState(Boolean(data.auto_trade))
      setPriceSeries((prev) => [...prev.slice(-99), data.price])
    }

    const timer = setInterval(refresh, 5000)
    return () => {
      clearInterval(timer)
      ws.close()
    }
  }, [])

  const onOpen = async (payload) => {
    try {
      await openTrade({ ...payload, quantity: Number(payload.quantity), lot_size: Number(payload.lot_size), target_profit_usd: Number(payload.target_profit_usd) })
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

  const onTrain = async () => {
    try {
      setTrainStats(await trainModel())
      setError('')
    } catch {
      setError('Training failed on backend')
    }
  }

  const onToggleAuto = async () => {
    try {
      const res = await setAutoTrade(!autoTrade)
      setAutoTradeState(res.enabled)
    } catch {
      setError('Failed to update auto-trade mode')
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 p-6 text-slate-100">
      <h1 className="mb-2 text-2xl font-bold">AurumBot XAUUSD</h1>
      <p className="mb-4 text-xs text-slate-400">WebSocket: {wsStatus} • Auto-trade threshold: 75% • News-hour lock: enabled</p>
      {error && <p className="mb-3 rounded bg-rose-900/50 p-2 text-sm">{error}</p>}

      <div className="mb-4 grid gap-4 lg:grid-cols-3">
        <SignalCard signal={signal} />
        <div className="rounded-xl bg-slate-900 p-4 shadow-lg">
          <h2 className="text-sm text-slate-400">Live Price / Spread (MT5 first)</h2>
          <p className="mt-2 text-3xl font-bold text-amber-400">{price?.price?.toFixed(2) || '--'}</p>
          <p className="text-sm text-slate-300">Bid: {price?.bid?.toFixed(2)} | Ask: {price?.ask?.toFixed(2)}</p>
          <p className="text-sm text-slate-300">Spread: {price?.spread?.toFixed(2)}</p>
          <p className="mt-2 text-sm">Trade status: <span className={activeTrade ? 'text-emerald-400' : 'text-slate-400'}>{activeTrade ? 'OPEN' : 'CLOSED'}</span></p>
          {activeTrade && (
            <>
              <p className="text-sm">PnL: <span className={activeTrade.pnl_usd >= 0 ? 'text-emerald-400' : 'text-rose-400'}>${activeTrade.pnl_usd.toFixed(2)}</span></p>
              <div className="mt-2 h-2 w-full rounded bg-slate-700"><div className="h-2 rounded bg-cyan-400" style={{ width: `${progress}%` }} /></div>
              <p className="mt-1 text-xs text-slate-400">Target progress (${target.toFixed(2)}): {progress.toFixed(1)}%</p>
            </>
          )}
          <div className="mt-3 flex gap-2">
            <button onClick={onTrain} className="rounded bg-indigo-600 px-3 py-1 text-xs font-semibold">Train 10Y Model</button>
            <button onClick={onToggleAuto} className={`rounded px-3 py-1 text-xs font-semibold ${autoTrade ? 'bg-emerald-700' : 'bg-slate-700'}`}>{autoTrade ? 'Disable Auto' : 'Enable Auto'}</button>
          </div>
          {trainStats && <p className="mt-2 text-xs text-slate-300">Rows: {trainStats.rows} | Accuracy: {(trainStats.accuracy * 100).toFixed(1)}% | Precision: {(trainStats.precision * 100).toFixed(1)}%</p>}
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
