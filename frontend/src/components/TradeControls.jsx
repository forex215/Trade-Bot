import { useState } from 'react'

export default function TradeControls({ onOpen, onClose, activeTrade }) {
  const [form, setForm] = useState({ side: '', quantity: 1, lot_size: 0.1, target_profit_usd: 10 })

  const update = (e) => setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))

  return (
    <div className="rounded-xl bg-slate-900 p-4 shadow-lg">
      <h2 className="mb-2 text-sm text-slate-400">Custom Trade Settings</h2>
      <div className="grid grid-cols-2 gap-2">
        <select name="side" value={form.side} onChange={update} className="rounded bg-slate-800 p-2 text-sm">
          <option value="">Auto (AI)</option>
          <option value="BUY">BUY</option>
          <option value="SELL">SELL</option>
        </select>
        <input name="quantity" value={form.quantity} onChange={update} type="number" step="0.1" className="rounded bg-slate-800 p-2 text-sm" placeholder="Quantity" />
        <input name="lot_size" value={form.lot_size} onChange={update} type="number" step="0.01" className="rounded bg-slate-800 p-2 text-sm" placeholder="Lot Size" />
        <input name="target_profit_usd" value={form.target_profit_usd} onChange={update} type="number" step="1" className="rounded bg-slate-800 p-2 text-sm" placeholder="Target PnL" />
      </div>

      <div className="mt-3 flex gap-2">
        <button onClick={() => onOpen(form)} className="rounded bg-emerald-600 px-4 py-2 text-sm font-semibold">Open Trade</button>
        <button
          onClick={() => activeTrade && onClose(activeTrade.trade_id)}
          disabled={!activeTrade}
          className="rounded bg-rose-600 px-4 py-2 text-sm font-semibold disabled:opacity-40"
        >
          Close Trade
        </button>
      </div>
    </div>
  )
}
