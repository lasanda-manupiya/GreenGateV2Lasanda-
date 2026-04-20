import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { TrajectoryPoint } from '../../types';

interface TrajectoryChartProps {
  data: TrajectoryPoint[];
  className?: string;
}

export function TrajectoryChart({ data, className = '' }: TrajectoryChartProps) {
  return (
    <div className={`w-full h-72 ${className}`}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis dataKey="year" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip
            contentStyle={{
              borderRadius: '8px',
              border: '1px solid var(--color-border)',
              fontSize: '12px',
            }}
          />
          <Legend wrapperStyle={{ fontSize: '12px' }} />
          <Line
            type="monotone"
            dataKey="target_emissions"
            name="Target"
            stroke="#1B6B3A"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="actual_emissions"
            name="Actual"
            stroke="#D4A843"
            strokeWidth={2}
            dot={{ r: 4 }}
            connectNulls={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
