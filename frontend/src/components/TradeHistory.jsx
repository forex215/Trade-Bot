export default function TradeHistory({ trades, activeTradeId }) {
  return (
    <div className="rounded-xl bg-slate-900 p-4 shadow-lg">
      <h2 className="mb-2 text-sm text-slate-400">Trade History</h2>
      <div className="max-h-72 overflow-auto text-sm">
        {trades.map((t) => (
          <div key={t.trade_id} className={`mb-2 rounded p-2 ${t.trade_id === activeTradeId ? 'bg-cyan-900/40' : 'bg-slate-800'}`}>
            <p className="font-semibold">{t.side} • {t.status}</p>
            <p>PnL: <span className={t.pnl_usd >= 0 ? 'text-emerald-400' : 'text-rose-400'}>${t.pnl_usd.toFixed(2)}</span></p>
            <p className="text-xs text-slate-400">{t.trade_id}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
