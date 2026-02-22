import { useApi } from '../hooks/useApi';
import { api } from '../lib/api';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';

function Table({ headers, rows }: { headers: string[]; rows: (string | number)[][] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 dark:border-gray-700">
            {headers.map((h) => (
              <th key={h} className="text-left py-2 px-3 font-medium text-gray-500 dark:text-gray-400">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50">
              {row.map((cell, j) => (
                <td key={j} className="py-2 px-3 text-gray-700 dark:text-gray-300">{typeof cell === 'number' ? cell.toLocaleString() : String(cell)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function SQLAnalysis() {
  const { data: totals, loading: l1 } = useApi(api.sqlTotal);
  const { data: topUsers, loading: l2 } = useApi(api.sqlTopUsers);
  const { data: perDay, loading: l3 } = useApi(api.sqlRecordsPerDay);
  const { data: latest, loading: l4 } = useApi(api.sqlLatestPerUser);

  const loading = l1 || l2 || l3 || l4;
  if (loading) return <div className="animate-pulse h-96 bg-gray-100 dark:bg-gray-800 rounded-2xl" />;

  return (
    <div className="space-y-6">
      {/* Query 1: Totals */}
      <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-800">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">Query 1: Total Records & Distinct Users</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-4 font-mono">SELECT COUNT(*) AS total_records, COUNT(DISTINCT user_id) AS distinct_users FROM sql_extract;</p>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-indigo-50 dark:bg-indigo-900/20 rounded-xl p-4 text-center">
            <p className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">{totals?.total_records?.toLocaleString()}</p>
            <p className="text-xs text-gray-500 mt-1">Total Records</p>
          </div>
          <div className="bg-emerald-50 dark:bg-emerald-900/20 rounded-xl p-4 text-center">
            <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{totals?.distinct_users?.toLocaleString()}</p>
            <p className="text-xs text-gray-500 mt-1">Distinct Users</p>
          </div>
        </div>
      </div>

      {/* Query 3: Top 5 users */}
      <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-800">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">Query 3: Top 5 Users by Record Count</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-4 font-mono">SELECT user_id, COUNT(*) AS record_count FROM sql_extract GROUP BY user_id ORDER BY record_count DESC LIMIT 5;</p>
        {topUsers && (
          <Table
            headers={['User ID', 'Record Count']}
            rows={topUsers.map((u) => [u.user_id, u.record_count])}
          />
        )}
      </div>

      {/* Query 4: Records per day */}
      <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-800">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">Query 4: Records Count Per Day</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-4 font-mono">SELECT CAST(ex_date AS DATE) AS record_date, COUNT(*) AS daily_count FROM sql_extract GROUP BY ... ORDER BY record_date;</p>
        {perDay && (
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={perDay}>
              <XAxis dataKey="record_date" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,.08)' }} />
              <Bar dataKey="daily_count" fill="#6366f1" radius={[4, 4, 0, 0]} name="Records" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Query 2: Latest per user (table) */}
      <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-800">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">Query 2: Latest Record Per User</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-4 font-mono">SELECT * FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY ex_date DESC) AS rn ...) WHERE rn = 1;</p>
        {latest && latest.length > 0 && (
          <div className="max-h-96 overflow-auto">
            <Table
              headers={Object.keys(latest[0])}
              rows={latest.map((r) => Object.values(r) as (string | number)[])}
            />
          </div>
        )}
      </div>
    </div>
  );
}
