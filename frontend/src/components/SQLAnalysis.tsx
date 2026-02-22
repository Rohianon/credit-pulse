import { useApi } from '../hooks/useApi';
import { api } from '../lib/api';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';
import { Terminal, Hash, Clock } from 'lucide-react';

function Table({ headers, rows }: { headers: string[]; rows: (string | number)[][] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b border-border-accent">
            {headers.map((h) => (
              <th key={h} className="text-left py-2.5 px-3 text-[10px] font-semibold uppercase tracking-[0.1em] text-text-muted">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-b border-border-subtle hover:bg-surface-overlay/50 transition-colors">
              {row.map((cell, j) => (
                <td key={j} className="py-2 px-3 text-text-secondary font-mono text-xs">
                  {typeof cell === 'number' ? cell.toLocaleString() : String(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function QueryCard({ number, title, sql, children }: { number: number; title: string; sql: string; children: React.ReactNode }) {
  return (
    <div className="bg-surface-raised rounded-xl border border-border-subtle noise relative overflow-hidden animate-fade-up" style={{ animationDelay: `${number * 80}ms` }}>
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-pz-green" />
      <div className="p-5">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-[10px] font-bold text-pz-green font-mono">Q{number}</span>
          <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
        </div>
        <div className="mt-2 mb-4 px-3 py-2 rounded-md bg-surface-overlay border border-border-subtle">
          <code className="text-[11px] text-text-muted font-mono leading-relaxed block whitespace-pre-wrap">{sql}</code>
        </div>
        {children}
      </div>
    </div>
  );
}

export default function SQLAnalysis() {
  const { data: totals, loading: l1 } = useApi(api.sqlTotal);
  const { data: topUsers, loading: l2 } = useApi(api.sqlTopUsers);
  const { data: perDay, loading: l3 } = useApi(api.sqlRecordsPerDay);
  const { data: latest, loading: l4 } = useApi(api.sqlLatestPerUser);

  const loading = l1 || l2 || l3 || l4;
  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-48 rounded-xl animate-shimmer" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-2">
        <Terminal className="w-4 h-4 text-pz-green" />
        <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-text-secondary">SQL Extract Analysis</h2>
        <span className="text-[10px] text-text-muted ml-auto font-mono">sql_extract.xlsx &middot; DuckDB</span>
      </div>

      {/* Query 1: Totals */}
      <QueryCard
        number={1}
        title="Total Records & Distinct Users"
        sql="SELECT COUNT(*) AS total_records, COUNT(DISTINCT user_id) AS distinct_users FROM raw_sql_extract;"
      >
        <div className="grid grid-cols-2 gap-3">
          <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-pz-green/8 border border-pz-green/15">
            <Hash className="w-4 h-4 text-pz-green shrink-0" />
            <div>
              <p className="text-xl font-bold font-mono text-text-primary">{totals?.total_records?.toLocaleString()}</p>
              <p className="text-[10px] text-text-muted uppercase tracking-wider">Total Records</p>
            </div>
          </div>
          <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-info/8 border border-info/15">
            <Hash className="w-4 h-4 text-info shrink-0" />
            <div>
              <p className="text-xl font-bold font-mono text-text-primary">{totals?.distinct_users?.toLocaleString()}</p>
              <p className="text-[10px] text-text-muted uppercase tracking-wider">Distinct Users</p>
            </div>
          </div>
        </div>
      </QueryCard>

      {/* Query 2: Latest per user */}
      <QueryCard
        number={2}
        title="Latest Record Per User"
        sql="SELECT * FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY ex_date DESC) AS rn FROM raw_sql_extract) WHERE rn = 1;"
      >
        {latest && latest.length > 0 && (
          <div className="max-h-80 overflow-auto rounded-lg border border-border-subtle">
            <Table
              headers={Object.keys(latest[0])}
              rows={latest.map((r) => Object.values(r) as (string | number)[])}
            />
          </div>
        )}
      </QueryCard>

      {/* Query 3: Top 5 users */}
      <QueryCard
        number={3}
        title="Top 5 Users by Record Count"
        sql="SELECT user_id, COUNT(*) AS record_count FROM raw_sql_extract GROUP BY user_id ORDER BY record_count DESC LIMIT 5;"
      >
        {topUsers && (
          <div className="rounded-lg border border-border-subtle overflow-hidden">
            <Table
              headers={['User ID', 'Record Count']}
              rows={topUsers.map((u) => [u.user_id, u.record_count])}
            />
          </div>
        )}
      </QueryCard>

      {/* Query 4: Records per day */}
      <QueryCard
        number={4}
        title="Records Count Per Day"
        sql="SELECT CAST(ex_date AS DATE) AS record_date, COUNT(*) AS daily_count FROM raw_sql_extract GROUP BY 1 ORDER BY record_date;"
      >
        <div className="flex items-center gap-1.5 mb-2">
          <Clock className="w-3 h-3 text-text-muted" />
          <span className="text-[10px] text-text-muted">Daily distribution</span>
        </div>
        {perDay && (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={perDay}>
              <XAxis dataKey="record_date" tick={{ fontSize: 9, fill: 'var(--color-text-muted)' }} interval="preserveStartEnd" axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: 'var(--color-text-muted)' }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{
                  background: 'var(--color-surface-raised)',
                  border: '1px solid var(--color-border-subtle)',
                  borderRadius: '8px',
                  fontSize: '11px',
                  color: 'var(--color-text-primary)',
                }}
              />
              <Bar dataKey="daily_count" fill="#4CB050" radius={[3, 3, 0, 0]} name="Records" opacity={0.85} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </QueryCard>
    </div>
  );
}
