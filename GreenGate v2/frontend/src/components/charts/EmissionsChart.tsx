import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface EmissionsChartProps {
  data: { scope: number; total: number }[];
  className?: string;
}

export function EmissionsChart({ data, className = '' }: EmissionsChartProps) {
  const chartData = [
    {
      name: 'Emissions by Scope',
      'Scope 1': data.find((d) => d.scope === 1)?.total || 0,
      'Scope 2': data.find((d) => d.scope === 2)?.total || 0,
      'Scope 3': data.find((d) => d.scope === 3)?.total || 0,
    },
  ];

  return (
    <div className={`w-full h-64 ${className}`}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip
            contentStyle={{
              borderRadius: '8px',
              border: '1px solid var(--color-border)',
              fontSize: '12px',
            }}
          />
          <Legend wrapperStyle={{ fontSize: '12px' }} />
          <Bar dataKey="Scope 1" fill="#1B6B3A" radius={[4, 4, 0, 0]} />
          <Bar dataKey="Scope 2" fill="#D4A843" radius={[4, 4, 0, 0]} />
          <Bar dataKey="Scope 3" fill="#6B7280" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
