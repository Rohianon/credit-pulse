import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { useApi } from '../../hooks/useApi';
import { api } from '../../lib/api';

export default function RiskSegments() {
  const { data, loading } = useApi(api.getSegments);
  if (loading || !data) return <div className="animate-pulse h-64 bg-gray-100 dark:bg-gray-800 rounded-xl" />;

  const chartData = data.map((d) => ({
    segment: d.risk_segment.replace('_', ' '),
    count: d.count,
    default_rate: Number((d.default_rate * 100).toFixed(1)),
  }));

  return (
    <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-800">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Risk Segments</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chartData}>
          <XAxis dataKey="segment" tick={{ fontSize: 12 }} />
          <YAxis yAxisId="left" tick={{ fontSize: 11 }} />
          <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11 }} unit="%" />
          <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,.08)' }} />
          <Legend />
          <Bar yAxisId="left" dataKey="count" fill="#6366f1" radius={[6, 6, 0, 0]} name="Borrowers" />
          <Bar yAxisId="right" dataKey="default_rate" fill="#ef4444" radius={[6, 6, 0, 0]} name="Default Rate %" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
