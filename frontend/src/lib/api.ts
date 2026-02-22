const BASE = '/api';

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init);
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`);
  return res.json();
}

export const api = {
  getOverview: () => fetchJson<Record<string, number>>(`${BASE}/insights/overview`),
  getFeatures: () => fetchJson<{ feature_importance: [string, number][]; model: string; auc: number }>(`${BASE}/insights/features`),
  getSegments: () => fetchJson<{ risk_segment: string; count: number; default_rate: number; avg_loan: number }[]>(`${BASE}/insights/segments`),
  getTransactions: () => fetchJson<{
    monthly_flows: { month: string; total_inflows: number; total_outflows: number; tx_count: number }[];
    categories: { tx_category: string; count: number; total_amount: number }[];
    hourly_distribution: { hour: number; count: number }[];
  }>(`${BASE}/insights/transactions`),
  getRepayment: () => fetchJson<{ status: string; count: number; avg_loan_amount: number }[]>(`${BASE}/insights/repayment`),
  getBetting: () => fetchJson<{ customer_id: number; betting_spend_ratio: number; is_defaulted: number; loan_amount: number }[]>(`${BASE}/insights/betting`),
  scoreRisk: (data: Record<string, number>) => fetchJson<{
    risk_score: number; risk_label: string; default_probability: number; model_used: string; top_factors: { feature: string; value: number; importance: number }[];
  }>(`${BASE}/score`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }),
  sqlTotal: () => fetchJson<{ total_records: number; distinct_users: number }>(`${BASE}/sql/total`),
  sqlLatestPerUser: () => fetchJson<Record<string, unknown>[]>(`${BASE}/sql/latest-per-user`),
  sqlTopUsers: () => fetchJson<{ user_id: number; record_count: number }[]>(`${BASE}/sql/top-users`),
  sqlRecordsPerDay: () => fetchJson<{ record_date: string; daily_count: number }[]>(`${BASE}/sql/records-per-day`),
};
