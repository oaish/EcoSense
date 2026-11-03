import React, { useState, useEffect } from 'react';
import { analyticsApi } from '../../api/analytics';
import { AnalyticsSummary, AlertItem } from '../../types';
import { StatCard } from '../../components/common/StatCard';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { StatusBadge } from '../../components/common/StatusBadge';
import { ProgressBar } from '../../components/common/ProgressBar';
import {
  LayoutDashboard,
  Recycle,
  Trash2,
  Users,
  AlertTriangle,
  Award,
  Layers,
  BarChart3,
  ArrowRight,
  ShieldCheck,
  MapPin,
  Sparkles,
} from 'lucide-react';
import {
  LuPackage,
  LuRecycle,
  LuGraduationCap,
  LuStar,
  LuLeaf,
  LuTriangleAlert,
  LuCircleCheck,
  LuTrash2,
  LuGift,
} from 'react-icons/lu';
import { Link } from 'react-router-dom';

import { safePercentage, formatWeight, formatNumber } from '../../utils/formatters';

export const AdminDashboard: React.FC = () => {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAdminDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [summaryRes, alertsRes] = await Promise.all([
        analyticsApi.getSummary().catch(() => null),
        analyticsApi.getAlerts().catch(() => []),
      ]);
      setSummary(summaryRes);
      setAlerts(alertsRes);
    } catch (err: any) {
      setError(err.message || 'Failed to load campus analytics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminDashboardData();
  }, []);

  if (loading) {
    return <LoadingState message="Loading campus sustainability control center..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={fetchAdminDashboardData} />;
  }

  // Safe calculated metrics
  const totalCollectedKg = summary?.summary?.total_collected_quantity_kg ?? 0;
  const totalRecycledKg = summary?.summary?.total_recycled_quantity_kg ?? 0;
  const totalCompostedKg = summary?.summary?.total_composted_quantity_kg ?? 0;
  const totalProcessedKg = totalRecycledKg + totalCompostedKg;
  
  const rawDiversion = summary?.summary?.diversion_rate;
  const diversionRate = rawDiversion != null
    ? Math.round(rawDiversion * 100)
    : totalCollectedKg > 0
    ? safePercentage(totalProcessedKg, totalCollectedKg)
    : 0;

  const totalDisposals = summary?.summary?.disposal_count ?? 0;
  const activeStudents = summary?.participation?.total_active_students ?? 0;
  const pointsDistributed = summary?.gamification?.total_points_earned ?? 0;
  const activeBins = summary?.operations?.active_bins ?? 0;
  const openReports = (summary?.operations?.pending_reports ?? 0) + (summary?.operations?.in_progress_reports ?? 0);

  return (
    <div className="max-w-6xl mx-auto py-4 space-y-8">
      {/* Control Center Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-black uppercase tracking-wider text-purple-800 bg-purple-100 px-3 py-1 rounded-full border border-purple-200">
              Admin Control Center
            </span>
            <span className="text-xs font-bold text-slate-500">DBIT Mumbai</span>
          </div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
            Campus Zero-Waste Overview
          </h1>
          <p className="text-slate-600 text-sm font-medium">
            Real-time telemetry, diversion rate metrics, and operational health monitoring.
          </p>
        </div>

        <Link
          to="/admin/analytics"
          className="btn-3d btn-3d-green px-6 py-3 text-xs font-black flex items-center justify-center gap-2 shadow-3d-green shrink-0"
        >
          <BarChart3 className="w-4 h-4" />
          <span>Full Analytics Suite</span>
        </Link>
      </div>

      {/* Top 4 KPI Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Waste Collected"
          value={formatWeight(totalCollectedKg)}
          subtitle={`${formatNumber(totalDisposals)} disposals logged`}
          icon={LuPackage}
          variant="green"
        />
        <StatCard
          title="Campus Diversion Rate"
          value={`${diversionRate}%`}
          subtitle="Recycled & Composted"
          icon={LuRecycle}
          variant="blue"
        />
        <StatCard
          title="Active Students"
          value={formatNumber(activeStudents)}
          subtitle="Registered campus contributors"
          icon={LuGraduationCap}
          variant="yellow"
        />
        <StatCard
          title="Points Distributed"
          value={formatNumber(pointsDistributed)}
          subtitle="Gamification ledger total"
          icon={LuStar}
          variant="yellow"
        />
      </div>

      {/* Secondary Operational Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard
          title="Active Bins Monitored"
          value={formatNumber(activeBins)}
          subtitle="Campus sensor & QR nodes"
          icon={Trash2}
          variant="slate"
        />
        <StatCard
          title="Open Waste Reports"
          value={formatNumber(openReports)}
          subtitle="Awaiting administrative action"
          icon={AlertTriangle}
          variant={openReports > 0 ? 'coral' : 'slate'}
        />
        <StatCard
          title="Recycled / Composted"
          value={formatWeight(totalProcessedKg)}
          subtitle={`${formatWeight(totalRecycledKg)} rec • ${formatWeight(totalCompostedKg)} comp`}
          icon={LuLeaf}
          variant="green"
        />
      </div>

      {/* Campus Diversion Progress Banner */}
      <div className="eco-card border-2 border-eco-300 p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="text-lg font-black text-slate-900">DBIT Campus Landfill Diversion</h3>
            <p className="text-xs text-slate-500 font-medium">
              Percentage of campus waste processed through composting & recycling rather than landfill.
            </p>
          </div>
          <span className="text-2xl font-black text-eco-700">{diversionRate}%</span>
        </div>
        <ProgressBar value={diversionRate} variant="green" showPercentage={false} />
      </div>

      {/* Derived Real-Time Operational Alerts */}
      <div className="eco-card space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-black text-slate-900 flex items-center gap-2">
            <LuTriangleAlert className="w-5 h-5 text-coral-600" />
            <span>Real-Time Operational Alerts</span>
          </h3>
          <span className="text-xs font-bold text-slate-400">
            {alerts.length} Active System Conditions
          </span>
        </div>

        {alerts.length === 0 ? (
          <div className="p-6 bg-eco-50 rounded-2xl border border-eco-200 text-center text-xs font-bold text-eco-800 flex items-center justify-center gap-2">
            <LuCircleCheck className="w-4 h-4 text-eco-600" />
            <span>All campus bins and operations are within normal thresholds.</span>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {alerts.map((alert, idx) => (
              <div
                key={idx}
                className="p-4 rounded-2xl border bg-slate-50 hover:bg-slate-100/80 transition-colors flex items-start gap-3.5"
              >
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center text-xl shrink-0 ${
                    alert.severity === 'HIGH' || alert.severity === 'CRITICAL'
                      ? 'bg-coral-100 text-coral-700 border border-coral-200'
                      : 'bg-amber-100 text-amber-700 border border-amber-200'
                  }`}
                >
                  <LuTriangleAlert className="w-5 h-5" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-black text-slate-900">{alert.title}</h4>
                    <span
                      className={`text-[10px] font-black uppercase px-2 py-0.5 rounded-full ${
                        alert.severity === 'HIGH' || alert.severity === 'CRITICAL'
                          ? 'bg-coral-100 text-coral-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}
                    >
                      {alert.severity}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 font-medium mt-1 leading-relaxed">
                    {alert.description}
                  </p>
                  {alert.location_name && (
                    <p className="text-[10px] font-bold text-slate-400 mt-1 flex items-center gap-1">
                      <MapPin className="w-3 h-3" />
                      <span>{alert.location_name}</span>
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick Administrative Management Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link
          to="/admin/bins"
          className="eco-card p-5 border-2 border-slate-200 hover:border-purple-300 transition-all flex flex-col justify-between group"
        >
          <div>
            <div className="w-10 h-10 rounded-2xl bg-purple-100 text-purple-700 flex items-center justify-center text-xl mb-3 group-hover:scale-105 transition-transform">
              <LuTrash2 className="w-5 h-5 text-purple-700" />
            </div>
            <h4 className="text-sm font-black text-slate-900">Manage Bins</h4>
            <p className="text-[11px] text-slate-500 font-medium mt-0.5">
              Deploy bins, assign locations & waste types.
            </p>
          </div>
          <div className="mt-3 flex items-center text-xs font-bold text-purple-700 gap-1">
            <span>Open Bins</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>

        <Link
          to="/admin/reports"
          className="eco-card p-5 border-2 border-slate-200 hover:border-coral-300 transition-all flex flex-col justify-between group"
        >
          <div>
            <div className="w-10 h-10 rounded-2xl bg-coral-100 text-coral-700 flex items-center justify-center text-xl mb-3 group-hover:scale-105 transition-transform">
              <LuTriangleAlert className="w-5 h-5 text-coral-700" />
            </div>
            <h4 className="text-sm font-black text-slate-900">Waste Reports</h4>
            <p className="text-[11px] text-slate-500 font-medium mt-0.5">
              Review and resolve campus problem reports.
            </p>
          </div>
          <div className="mt-3 flex items-center text-xs font-bold text-coral-700 gap-1">
            <span>Resolve Reports</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>

        <Link
          to="/admin/rewards"
          className="eco-card p-5 border-2 border-slate-200 hover:border-sun-300 transition-all flex flex-col justify-between group"
        >
          <div>
            <div className="w-10 h-10 rounded-2xl bg-sun-100 text-sun-800 flex items-center justify-center text-xl mb-3 group-hover:scale-105 transition-transform">
              <LuGift className="w-5 h-5 text-sun-700" />
            </div>
            <h4 className="text-sm font-black text-slate-900">Rewards Catalog</h4>
            <p className="text-[11px] text-slate-500 font-medium mt-0.5">
              Create student perks and manage store inventory.
            </p>
          </div>
          <div className="mt-3 flex items-center text-xs font-bold text-sun-800 gap-1">
            <span>Manage Store</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>

        <Link
          to="/admin/points"
          className="eco-card p-5 border-2 border-slate-200 hover:border-eco-300 transition-all flex flex-col justify-between group"
        >
          <div>
            <div className="w-10 h-10 rounded-2xl bg-eco-100 text-eco-700 flex items-center justify-center text-xl mb-3 group-hover:scale-105 transition-transform">
              <LuStar className="w-5 h-5 text-eco-700" />
            </div>
            <h4 className="text-sm font-black text-slate-900">Points Ledger</h4>
            <p className="text-[11px] text-slate-500 font-medium mt-0.5">
              Inspect user balances & execute ledger adjustments.
            </p>
          </div>
          <div className="mt-3 flex items-center text-xs font-bold text-eco-700 gap-1">
            <span>View Ledger</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>
      </div>
    </div>
  );
};
