import {
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend)

export default function PriceChart({ points }) {
  const data = {
    labels: points.map((_, i) => i + 1),
    datasets: [
      {
        label: 'XAUUSD',
        data: points,
        borderColor: '#22d3ee',
        backgroundColor: '#22d3ee33',
        tension: 0.3,
      },
    ],
  }

  return (
    <div className="rounded-xl bg-slate-900 p-4 shadow-lg">
      <h2 className="mb-2 text-sm text-slate-400">Live Chart</h2>
      <Line data={data} />
    </div>
  )
}
