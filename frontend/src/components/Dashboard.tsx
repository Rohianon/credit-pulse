import { useApi } from '../hooks/useApi';
import { api } from '../lib/api';
import { Users, AlertTriangle, Banknote, TrendingUp } from 'lucide-react';
import RepaymentDistribution from './charts/RepaymentDistribution';
import FeatureImportance from './charts/FeatureImportance';
import RiskSegments from './charts/RiskSegments';
import TransactionFlows from './charts/TransactionFlows';
import CategoryBreakdown from './charts/CategoryBreakdown';
import BettingCorrelation from './charts/BettingCorrelation';

function StatCard({
  icon: Icon,
  label,
  value,
  sub,
  accent,
  delay,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
  sub?: string;
  accent: string;
  delay: number;
}) {
  return (
    <div
      className="relative group bg-surface-raised rounded-xl p-5 border border-border-subtle card-hover overflow-hidden noise animate-fade-up"
      style={{ animationDelay: `${delay}ms` }}
    >
      {/* Colored top edge */}
      <div className={`absolute top-0 left-0 right-0 h-[2px] ${accent}`} />

      <div className="flex items-center justify-between mb-4">
        <span className="text-[11px] font-medium uppercase tracking-[0.12em] text-text-muted">{label}</span>
        <Icon className="w-4 h-4 text-text-muted" />
      </div>
      <p className="text-2xl font-bold tracking-tight text-text-primary font-mono">{value}</p>
      {sub && <p className="text-[11px] text-text-muted mt-1.5">{sub}</p>}
    </div>
  );
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-3 mb-4 mt-2">
      <div className="w-1 h-4 rounded-full bg-pz-green" />
      <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-text-secondary">{children}</h2>
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
          <div key={i} className="h-28 rounded-xl animate-shimmer" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stat cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={Users}
          label="Borrowers"
          value={overview?.total_borrowers?.toFixed(0) ?? '—'}
          sub="Active in portfolio"
          accent="bg-pz-green"
          delay={0}
        />
        <StatCard
          icon={AlertTriangle}
          label="Default Rate"
          value={`${((overview?.default_rate ?? 0) * 100).toFixed(1)}%`}
          sub={`${overview?.total_defaults?.toFixed(0) ?? 0} borrowers defaulted`}
          accent="bg-danger"
          delay={60}
        />
        <StatCard
          icon={Banknote}
          label="Avg Loan"
          value={`KES ${(overview?.avg_loan_amount ?? 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
          sub={`KES ${(overview?.total_disbursed ?? 0).toLocaleString(undefined, { maximumFractionDigits: 0 })} total`}
          accent="bg-warning"
          delay={120}
        />
        <StatCard
          icon={TrendingUp}
          label="Model AUC"
          value={features?.auc?.toFixed(3) ?? '—'}
          sub={features?.model?.replace(/_/g, ' ') ?? ''}
          accent="bg-info"
          delay={180}
        />
      </div>

      {/* Portfolio Overview */}
      <SectionLabel>Portfolio Overview</SectionLabel>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <RepaymentDistribution />
        <FeatureImportance />
      </div>

      {/* Risk Analysis */}
      <SectionLabel>Risk Analysis</SectionLabel>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <RiskSegments />
        <BettingCorrelation />
      </div>

      {/* Transaction Intelligence */}
      <SectionLabel>Transaction Intelligence</SectionLabel>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <TransactionFlows />
        <CategoryBreakdown />
      </div>
    </div>
  );
}
