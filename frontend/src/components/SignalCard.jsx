export default function SignalCard({ signal }) {
  const color = signal?.signal === 'BUY' ? 'text-emerald-400' : signal?.signal === 'SELL' ? 'text-rose-400' : 'text-yellow-400'

  return (
    <div className="rounded-xl bg-slate-900 p-4 shadow-lg">
      <h2 className="text-sm text-slate-400">Current AI Signal</h2>
      <p className={`mt-2 text-3xl font-bold ${color}`}>{signal?.signal || '...'}</p>
      <p className="mt-2 text-sm text-slate-300">Confidence: {((signal?.confidence || 0) * 100).toFixed(1)}%</p>
      <p className="text-sm text-emerald-300">Win chance: {((signal?.win_probability || 0) * 100).toFixed(1)}%</p>
      <p className="text-sm text-rose-300">Lose chance: {((signal?.lose_probability || 0) * 100).toFixed(1)}%</p>
      <p className="mt-2 text-xs text-slate-400">{signal?.reason}</p>
    </div>
  )
}
