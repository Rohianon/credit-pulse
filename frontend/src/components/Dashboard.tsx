import { useApi } from '../hooks/useApi';
import { api } from '../lib/api';
import { Users, AlertTriangle, Banknote, TrendingUp } from 'lucide-react';
import RepaymentDistribution from './charts/RepaymentDistribution';
import FeatureImportance from './charts/FeatureImportance';
import RiskSegments from './charts/RiskSegments';
import TransactionFlows from './charts/TransactionFlows';
import CategoryBreakdown from './charts/CategoryBreakdown';
import BettingCorrelation from './charts/BettingCorrelation';

function StatCard({ icon: Icon, label, value, sub, color }: { icon: React.ComponentType<{ className?: string }>; label: string; value: string; sub?: string; color: string }) {
  return (
    <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-800">
      <div className="flex items-center gap-3 mb-3">
        <div className={`p-2.5 rounded-xl ${color}`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">{label}</span>
      </div>
      <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  );
}

export default function Dashboard() {
  const { data: overview, loading } = useApi(api.getOverview);
  const { data: features } = useApi(api.getFeatures);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="animate-pulse h-32 bg-gray-100 dark:bg-gray-800 rounded-2xl" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stat cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Users} label="Total Borrowers" value={overview?.total_borrowers?.toFixed(0) ?? '—'} color="bg-indigo-500" />
        <StatCard icon={AlertTriangle} label="Default Rate" value={`${((overview?.default_rate ?? 0) * 100).toFixed(1)}%`} sub={`${overview?.total_defaults?.toFixed(0) ?? 0} defaults`} color="bg-red-500" />
        <StatCard icon={Banknote} label="Avg Loan Amount" value={`KES ${(overview?.avg_loan_amount ?? 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}`} color="bg-amber-500" />
        <StatCard icon={TrendingUp} label="Model AUC" value={features?.auc?.toFixed(3) ?? '—'} sub={features?.model?.replace(/_/g, ' ') ?? ''} color="bg-emerald-500" />
      </div>

      {/* Charts row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RepaymentDistribution />
        <FeatureImportance />
      </div>

      {/* Charts row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RiskSegments />
        <TransactionFlows />
      </div>

      {/* Charts row 3 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CategoryBreakdown />
        <BettingCorrelation />
      </div>
    </div>
  );
}
