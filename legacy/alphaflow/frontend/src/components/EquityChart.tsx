import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { format } from 'date-fns'

interface EquityPoint {
  date: string
  equity: number
}

interface EquityChartProps {
  data: EquityPoint[]
}

export default function EquityChart({ data }: EquityChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-80 flex items-center justify-center text-text-secondary">
        No data available
      </div>
    )
  }

  // Format data for Recharts
  const chartData = data.map((point) => ({
    ...point,
    date: new Date(point.date).getTime(),
  }))

  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2A2E39" />
        <XAxis
          dataKey="date"
          type="number"
          domain={['dataMin', 'dataMax']}
          tickFormatter={(timestamp) => format(new Date(timestamp), 'MMM d')}
          stroke="#848E9C"
          style={{ fontSize: '12px' }}
        />
        <YAxis
          stroke="#848E9C"
          style={{ fontSize: '12px' }}
          tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#131722',
            border: '1px solid #2A2E39',
            borderRadius: '8px',
            padding: '12px',
          }}
          labelStyle={{ color: '#E0E3EB', marginBottom: '8px' }}
          itemStyle={{ color: '#2962FF' }}
          labelFormatter={(timestamp) => format(new Date(timestamp), 'MMM d, yyyy')}
          formatter={(value: number) => [`$${value.toLocaleString()}`, 'Equity']}
        />
        <Line
          type="monotone"
          dataKey="equity"
          stroke="#2962FF"
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 6, fill: '#2962FF' }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
