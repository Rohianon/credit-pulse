import { AreaChart, Area, XAxis, YAxis, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { useApi } from '../../hooks/useApi';
import { api } from '../../lib/api';

export default function TransactionFlows() {
  const { data, loading } = useApi(api.getTransactions);
  if (loading || !data) return <div className="animate-pulse h-64 bg-gray-100 dark:bg-gray-800 rounded-xl" />;

  const chartData = data.monthly_flows.map((d) => ({
    month: d.month,
    inflows: Math.round(d.total_inflows),
    outflows: Math.round(d.total_outflows),
  }));

  return (
    <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-800">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Monthly Transaction Flows</h3>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="inG" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="outG" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis dataKey="month" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
          <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `${(v / 1e6).toFixed(1)}M`} />
          <Tooltip formatter={(v) => `KES ${Number(v).toLocaleString()}`} contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,.08)' }} />
          <Legend />
          <Area type="monotone" dataKey="inflows" stroke="#22c55e" fill="url(#inG)" strokeWidth={2} name="Inflows" />
          <Area type="monotone" dataKey="outflows" stroke="#ef4444" fill="url(#outG)" strokeWidth={2} name="Outflows" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
