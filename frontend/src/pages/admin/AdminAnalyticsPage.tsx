import React, { useState, useEffect } from 'react';
import { analyticsApi } from '../../api/analytics';
import {
  AnalyticsSummary,
  WasteTypeMetric,
  LocationMetric,
  TrendAnalytics,
  CollectionAnalytics,
  BinFillAnalytics,
  ReportAnalytics,
  ProcessingAnalytics,
  ParticipationAnalytics,
  GamificationAnalytics,
  PredictionAnalytics,
  ClassificationAnalytics,
} from '../../types';
import { StatCard } from '../../components/common/StatCard';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { ProgressBar } from '../../components/common/ProgressBar';
import { StatusBadge } from '../../components/common/StatusBadge';
import {
  BarChart3,
  PieChart,
  MapPin,
  TrendingUp,
  Layers,
  Trash2,
  AlertTriangle,
  Recycle,
  Users,
  Award,
  Sparkles,
  Bot,
  Calendar,
} from 'lucide-react';
import {
  LuLayoutDashboard,
  LuRecycle,
  LuMapPin,
  LuTrendingUp,
  LuTruck,
  LuTrash2,
  LuTriangleAlert,
  LuLeaf,
  LuGraduationCap,
  LuStar,
  LuSparkles,
  LuBot,
  LuPackage,
  LuClock,
  LuRotateCw,
  LuCircleCheck,
  LuGift,
  LuCoins,
  LuTarget,
} from 'react-icons/lu';

import { safePercentage, formatPercentage, formatWeight, formatNumber } from '../../utils/formatters';

type AnalyticsTab =
  | 'overview'
  | 'waste-types'
  | 'locations'
  | 'trends'
  | 'collections'
  | 'bin-fill'
  | 'reports'
  | 'processing'
  | 'participation'
  | 'gamification'
  | 'predictions'
  | 'classifications';

export const AdminAnalyticsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<AnalyticsTab>('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Analytics State
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [wasteTypes, setWasteTypes] = useState<WasteTypeMetric[]>([]);
  const [locations, setLocations] = useState<LocationMetric[]>([]);
  const [trends, setTrends] = useState<TrendAnalytics | null>(null);
  const [collections, setCollections] = useState<CollectionAnalytics | null>(null);
  const [binFill, setBinFill] = useState<BinFillAnalytics | null>(null);
  const [reports, setReports] = useState<ReportAnalytics | null>(null);
  const [processing, setProcessing] = useState<ProcessingAnalytics | null>(null);
  const [participation, setParticipation] = useState<ParticipationAnalytics | null>(null);
  const [gamification, setGamification] = useState<GamificationAnalytics | null>(null);
  const [predictions, setPredictions] = useState<PredictionAnalytics | null>(null);
  const [classifications, setClassifications] = useState<ClassificationAnalytics | null>(null);

  const fetchAllAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const [
        summaryRes,
        wtRes,
        locRes,
        trendRes,
        colRes,
        fillRes,
        repRes,
        procRes,
        partRes,
        gamRes,
        predRes,
        classRes,
      ] = await Promise.all([
        analyticsApi.getSummary().catch(() => null),
        analyticsApi.getWasteTypes().catch(() => []),
        analyticsApi.getLocations().catch(() => []),
        analyticsApi.getTrends({ granularity: 'day' }).catch(() => null),
        analyticsApi.getCollections().catch(() => null),
        analyticsApi.getBinFill().catch(() => null),
        analyticsApi.getReports().catch(() => null),
        analyticsApi.getProcessing().catch(() => null),
        analyticsApi.getParticipation().catch(() => null),
        analyticsApi.getGamification().catch(() => null),
        analyticsApi.getPredictions().catch(() => null),
        analyticsApi.getClassifications().catch(() => null),
      ]);

      setSummary(summaryRes);
      setWasteTypes(wtRes);
      setLocations(locRes);
      setTrends(trendRes);
      setCollections(colRes);
      setBinFill(fillRes);
      setReports(repRes);
      setProcessing(procRes);
      setParticipation(partRes);
      setGamification(gamRes);
      setPredictions(predRes);
      setClassifications(classRes);
    } catch (err: any) {
      setError(err.message || 'Failed to retrieve analytics telemetry.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllAnalytics();
  }, []);

  if (loading) {
    return <LoadingState message="Aggregating campus analytics & telemetry..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={fetchAllAnalytics} />;
  }

  const tabs: { id: AnalyticsTab; label: string; icon: React.ReactNode }[] = [
    { id: 'overview', label: 'Summary', icon: <LuLayoutDashboard className="w-4 h-4" /> },
    { id: 'waste-types', label: 'Waste Streams', icon: <LuRecycle className="w-4 h-4" /> },
    { id: 'locations', label: 'Locations', icon: <LuMapPin className="w-4 h-4" /> },
    { id: 'trends', label: 'Trends', icon: <LuTrendingUp className="w-4 h-4" /> },
    { id: 'collections', label: 'Collections', icon: <LuTruck className="w-4 h-4" /> },
    { id: 'bin-fill', label: 'Bin Fill', icon: <LuTrash2 className="w-4 h-4" /> },
    { id: 'reports', label: 'Reports', icon: <LuTriangleAlert className="w-4 h-4" /> },
    { id: 'processing', label: 'Processing', icon: <LuLeaf className="w-4 h-4" /> },
    { id: 'participation', label: 'Participation', icon: <LuGraduationCap className="w-4 h-4" /> },
    { id: 'gamification', label: 'Gamification', icon: <LuStar className="w-4 h-4" /> },
    { id: 'predictions', label: 'Predictions', icon: <LuSparkles className="w-4 h-4" /> },
    { id: 'classifications', label: 'AI Classifications', icon: <LuBot className="w-4 h-4" /> },
  ];

  // Overview metrics calculation
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

  const recycledPct = totalCollectedKg > 0 ? safePercentage(totalRecycledKg, totalCollectedKg) : 0;
  const compostedPct = totalCollectedKg > 0 ? safePercentage(totalCompostedKg, totalCollectedKg) : 0;

  return (
    <div className="max-w-6xl mx-auto py-4 space-y-6">
      {/* Header */}
      <div>
        <span className="text-xs font-black uppercase tracking-wider text-purple-800 bg-purple-100 px-3 py-1 rounded-full border border-purple-200">
          Executive Analytics Suite
        </span>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
          Campus Sustainability Analytics
        </h1>
        <p className="text-slate-600 text-sm font-medium">
          Comprehensive data layer across all DBIT zero-waste operations (Phases 1–9).
        </p>
      </div>

      {/* Tab Selector */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-2 scrollbar-none">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-3.5 py-2 rounded-2xl text-xs font-black whitespace-nowrap transition-all flex items-center gap-1.5 ${
              activeTab === tab.id
                ? 'bg-purple-600 text-white shadow-3d-slate translate-y-0.5'
                : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
            }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* TAB CONTENT: Overview */}
      {activeTab === 'overview' && summary && (
        <div className="space-y-6 animate-in fade-in">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Total Waste Collected"
              value={formatWeight(totalCollectedKg)}
              subtitle={`${formatNumber(summary.summary?.disposal_count ?? 0)} student disposals`}
              icon={LuPackage}
              variant="green"
            />
            <StatCard
              title="Campus Diversion Rate"
              value={`${diversionRate}%`}
              subtitle="Landfill diversion"
              icon={LuRecycle}
              variant="blue"
            />
            <StatCard
              title="Active Students"
              value={formatNumber(summary.participation?.total_active_students ?? 0)}
              subtitle={`${formatNumber(summary.participation?.participating_students ?? 0)} active participants`}
              icon={LuGraduationCap}
              variant="yellow"
            />
            <StatCard
              title="Points Distributed"
              value={formatNumber(summary.gamification?.total_points_earned ?? 0)}
              subtitle={`${formatNumber(summary.gamification?.total_points_redeemed ?? 0)} redeemed`}
              icon={LuStar}
              variant="yellow"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="eco-card space-y-4">
              <h3 className="text-base font-black text-slate-900">Campus Waste Diversion Breakdown</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between text-xs font-bold">
                  <span className="text-slate-600">Recycled Waste</span>
                  <span className="text-ocean-700">{formatWeight(totalRecycledKg)}</span>
                </div>
                <ProgressBar
                  value={recycledPct}
                  variant="blue"
                  showPercentage={true}
                />

                <div className="flex items-center justify-between text-xs font-bold pt-2">
                  <span className="text-slate-600">Composted Organic Waste</span>
                  <span className="text-eco-700">{formatWeight(totalCompostedKg)}</span>
                </div>
                <ProgressBar
                  value={compostedPct}
                  variant="green"
                  showPercentage={true}
                />
              </div>
            </div>

            <div className="eco-card space-y-4">
              <h3 className="text-base font-black text-slate-900">Infrastructure & System State</h3>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-200">
                  <p className="text-slate-400 font-bold uppercase text-[10px]">Active Bins</p>
                  <p className="text-2xl font-black text-slate-900 mt-1">
                    {formatNumber(summary.operations?.active_bins ?? 0)}
                  </p>
                </div>
                <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-200">
                  <p className="text-slate-400 font-bold uppercase text-[10px]">High Fill Bins</p>
                  <p className="text-2xl font-black text-amber-700 mt-1">
                    {formatNumber(summary.operations?.high_fill_bins ?? 0)}
                  </p>
                </div>
                <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-200">
                  <p className="text-slate-400 font-bold uppercase text-[10px]">Open Reports</p>
                  <p className="text-2xl font-black text-coral-700 mt-1">
                    {formatNumber((summary.operations?.pending_reports ?? 0) + (summary.operations?.in_progress_reports ?? 0))}
                  </p>
                </div>
                <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-200">
                  <p className="text-slate-400 font-bold uppercase text-[10px]">Total Disposals</p>
                  <p className="text-2xl font-black text-eco-700 mt-1">
                    {formatNumber(summary.summary?.disposal_count ?? 0)}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT: Waste Types */}
      {activeTab === 'waste-types' && (
        <div className="eco-card space-y-6 animate-in fade-in">
          <h3 className="text-lg font-black text-slate-900">Waste Streams Categorization</h3>
          {wasteTypes.length === 0 ? (
            <div className="p-8 text-center text-slate-500 font-bold text-xs bg-slate-50 rounded-2xl border border-slate-200">
              No waste stream records logged for this period.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {wasteTypes.map((wt) => (
                <div
                  key={wt.waste_type_id}
                  className="p-4 rounded-2xl border-2 bg-slate-50 space-y-3"
                  style={{ borderColor: '#10B981' }}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-black text-slate-900">{wt.waste_type_name}</span>
                    <span className="text-xs font-black text-slate-700">
                      {formatWeight(wt.collected_quantity_kg ?? 0)} collected
                    </span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-center text-xs">
                    <div className="p-2 bg-white rounded-xl border border-slate-200">
                      <p className="text-[10px] text-slate-400 font-bold">Disposals</p>
                      <p className="font-extrabold text-slate-800">{formatNumber(wt.disposal_count)}</p>
                    </div>
                    <div className="p-2 bg-white rounded-xl border border-slate-200">
                      <p className="text-[10px] text-slate-400 font-bold">Recycled</p>
                      <p className="font-extrabold text-ocean-700">{formatWeight(wt.recycled_quantity_kg ?? 0)}</p>
                    </div>
                    <div className="p-2 bg-white rounded-xl border border-slate-200">
                      <p className="text-[10px] text-slate-400 font-bold">Composted</p>
                      <p className="font-extrabold text-eco-700">{formatWeight(wt.composted_quantity_kg ?? 0)}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB CONTENT: Locations */}
      {activeTab === 'locations' && (
        <div className="eco-card space-y-4 animate-in fade-in">
          <h3 className="text-lg font-black text-slate-900">Waste Activity by Campus Location</h3>
          {locations.length === 0 ? (
            <div className="p-8 text-center text-slate-500 font-bold text-xs bg-slate-50 rounded-2xl border border-slate-200">
              No campus locations found.
            </div>
          ) : (
            <div className="space-y-3">
              {locations.map((loc) => (
                <div
                  key={loc.location_id}
                  className="p-4 rounded-2xl bg-slate-50 border border-slate-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div>
                    <h4 className="text-sm font-black text-slate-900">{loc.location_name}</h4>
                    <p className="text-xs text-slate-500 font-semibold">
                      {loc.building || 'Campus'} • {loc.floor || 'Floor'} • {formatNumber(loc.active_bin_count)} active bins
                    </p>
                  </div>
                  <div className="flex items-center gap-4 text-xs font-extrabold">
                    <div className="text-right">
                      <p className="text-slate-400 text-[10px] uppercase">Collected</p>
                      <p className="text-slate-900">{formatWeight(loc.collected_quantity_kg ?? 0)}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-slate-400 text-[10px] uppercase">Avg Fill</p>
                      <p className="text-eco-700">{formatPercentage(loc.average_fill_percentage ?? 0)}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-slate-400 text-[10px] uppercase">Disposals</p>
                      <p className="text-purple-700">{formatNumber(loc.disposal_count)}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB CONTENT: Trends */}
      {activeTab === 'trends' && (
        <div className="eco-card space-y-4 animate-in fade-in">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-black text-slate-900">Campus Activity Trends</h3>
            <span className="text-xs font-bold text-slate-400 capitalize">
              Granularity: {trends?.granularity || 'day'}
            </span>
          </div>

          {!trends || trends.data_points.length === 0 ? (
            <div className="p-8 text-center text-slate-500 font-bold text-xs bg-slate-50 rounded-2xl border border-slate-200">
              No trend data available for this period.
            </div>
          ) : (
            <div className="space-y-2">
              {trends.data_points.map((pt, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-slate-50 rounded-2xl border border-slate-200 flex items-center justify-between text-xs"
                >
                  <span className="font-bold text-slate-700">{pt.period}</span>
                  <div className="flex items-center gap-4 font-extrabold">
                    <span className="text-slate-600">{formatNumber(pt.disposal_count)} disposals</span>
                    <span className="text-amber-700">{formatWeight(pt.collected_quantity_kg ?? 0)} collected</span>
                    <span className="text-ocean-700">{formatWeight(pt.recycled_quantity_kg ?? 0)} recycled</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB CONTENT: Collections */}
      {activeTab === 'collections' && (
        <div className="space-y-6 animate-in fade-in">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <StatCard
              title="Total Collected"
              value={formatWeight(collections?.total_collected_quantity_kg ?? 0)}
              subtitle={`${formatNumber(collections?.total_collections ?? 0)} collection operations`}
              icon={Layers}
              variant="green"
            />
            <StatCard
              title="Avg Fill Reduction"
              value={formatPercentage((collections?.average_fill_before ?? 0) - (collections?.average_fill_after ?? 0))}
              subtitle={`From ${formatPercentage(collections?.average_fill_before ?? 0)} to ${formatPercentage(collections?.average_fill_after ?? 0)}`}
              icon={Trash2}
              variant="yellow"
            />
            <StatCard
              title="Avg Batch Weight"
              value={formatWeight(collections?.average_collected_quantity_kg ?? 0)}
              subtitle="Per collection event"
              icon={Recycle}
              variant="blue"
            />
          </div>

          <div className="eco-card space-y-3">
            <h3 className="text-base font-black text-slate-900">Frequently Serviced Bins</h3>
            {!collections || collections.frequently_collected_bins.length === 0 ? (
              <div className="p-6 text-center text-slate-500 font-bold text-xs bg-slate-50 rounded-2xl border border-slate-200">
                No bin collection records logged yet.
              </div>
            ) : (
              <div className="space-y-2">
                {collections.frequently_collected_bins.map((tb) => (
                  <div
                    key={tb.bin_id}
                    className="p-3 bg-slate-50 rounded-2xl border border-slate-200 flex items-center justify-between text-xs font-bold"
                  >
                    <div>
                      <span className="font-black text-slate-900">{tb.bin_code}</span>
                      <span className="text-slate-400 ml-2">({tb.location_name})</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-slate-600">{formatNumber(tb.collection_count)} collections</span>
                      <span className="text-amber-800 font-extrabold">{formatWeight(tb.total_kg)}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB CONTENT: Bin Fill */}
      {activeTab === 'bin-fill' && (
        <div className="space-y-6 animate-in fade-in">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <StatCard
              title="Total Readings"
              value={formatNumber(binFill?.total_readings ?? 0)}
              subtitle="Telemetry data points"
              icon={Trash2}
              variant="slate"
            />
            <StatCard
              title="Avg Fill Level"
              value={formatPercentage(binFill?.average_fill_percentage ?? 0)}
              subtitle="Campus-wide average"
              icon={BarChart3}
              variant="green"
            />
            <StatCard
              title="High Fill (≥ 80%)"
              value={formatNumber(binFill?.high_fill_reading_count ?? 0)}
              subtitle="Critical readings"
              icon={AlertTriangle}
              variant="coral"
            />
          </div>

          <div className="eco-card space-y-3">
            <h3 className="text-base font-black text-slate-900">Critical High-Fill Bins</h3>
            {!binFill || binFill.high_fill_bins.length === 0 ? (
              <div className="p-6 text-center text-slate-500 font-bold text-xs bg-slate-50 rounded-2xl border border-slate-200">
                All campus bins are currently within normal capacity limits.
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {binFill.high_fill_bins.map((cb) => (
                  <div
                    key={cb.bin_id}
                    className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-black text-slate-900">{cb.bin_code}</span>
                      <span className="text-xs font-black text-coral-600">
                        {formatPercentage(cb.current_fill_percentage ?? 0)} Full
                      </span>
                    </div>
                    <ProgressBar value={cb.current_fill_percentage ?? 0} variant="coral" />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB CONTENT: Reports */}
      {activeTab === 'reports' && (
        <div className="space-y-6 animate-in fade-in">
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
            <StatCard
              title="Total Reports"
              value={formatNumber(reports?.total_reports ?? 0)}
              icon={AlertTriangle}
              variant="slate"
            />
            <StatCard
              title="Pending"
              value={formatNumber(reports?.pending_reports ?? 0)}
              icon={LuClock}
              variant="coral"
            />
            <StatCard
              title="In Progress"
              value={formatNumber(reports?.in_progress_reports ?? 0)}
              icon={LuRotateCw}
              variant="yellow"
            />
            <StatCard
              title="Resolved"
              value={formatNumber(reports?.resolved_reports ?? 0)}
              icon={LuCircleCheck}
              variant="green"
            />
          </div>

          <div className="eco-card space-y-3">
            <h3 className="text-base font-black text-slate-900">Reports by Category</h3>
            {!reports || Object.keys(reports.reports_by_type).length === 0 ? (
              <div className="p-6 text-center text-slate-500 font-bold text-xs bg-slate-50 rounded-2xl border border-slate-200">
                No waste reports recorded.
              </div>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {Object.entries(reports.reports_by_type).map(([type, count]) => (
                  <div key={type} className="p-3.5 bg-slate-50 rounded-2xl border border-slate-200">
                    <p className="text-[10px] uppercase font-bold text-slate-400 capitalize">
                      {type.replace(/_/g, ' ')}
                    </p>
                    <p className="text-2xl font-black text-slate-900 mt-1">{formatNumber(count)}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB CONTENT: Processing */}
      {activeTab === 'processing' && (
        <div className="space-y-6 animate-in fade-in">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <StatCard
              title="Total Processed"
              value={formatWeight(processing?.total_processed_quantity_kg ?? 0)}
              subtitle="Diverted from landfill"
              icon={Recycle}
              variant="green"
            />
            <StatCard
              title="Recycled Batches"
              value={formatWeight(processing?.total_recycled_quantity_kg ?? 0)}
              subtitle="Recycling facility streams"
              icon={LuRecycle}
              variant="blue"
            />
            <StatCard
              title="Composted Batches"
              value={formatWeight(processing?.total_composted_quantity_kg ?? 0)}
              subtitle="Campus compost units"
              icon={LuLeaf}
              variant="yellow"
            />
          </div>
        </div>
      )}

      {/* TAB CONTENT: Participation */}
      {activeTab === 'participation' && (
        <div className="space-y-6 animate-in fade-in">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <StatCard
              title="Active Students"
              value={formatNumber(participation?.total_active_students ?? 0)}
              subtitle={`Out of all registered accounts`}
              icon={Users}
              variant="yellow"
            />
            <StatCard
              title="Participation Rate"
              value={formatPercentage(participation?.participation_rate ? participation.participation_rate * 100 : 0)}
              subtitle="Campus engagement"
              icon={LuTrendingUp}
              variant="green"
            />
            <StatCard
              title="Student Disposals"
              value={formatNumber(participation?.disposal_records_count ?? 0)}
              subtitle="Verified QR events"
              icon={LuLeaf}
              variant="blue"
            />
          </div>
        </div>
      )}

      {/* TAB CONTENT: Gamification */}
      {activeTab === 'gamification' && (
        <div className="space-y-6 animate-in fade-in">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <StatCard
              title="Points Awarded"
              value={formatNumber(gamification?.total_points_earned ?? 0)}
              subtitle="Lifetime distributed"
              icon={LuStar}
              variant="yellow"
            />
            <StatCard
              title="Points Redeemed"
              value={formatNumber(gamification?.total_points_redeemed ?? 0)}
              subtitle="Spent by students"
              icon={LuGift}
              variant="green"
            />
            <StatCard
              title="Redemption Events"
              value={formatNumber(gamification?.reward_redemptions_count ?? 0)}
              subtitle="Store claims fulfilled"
              icon={LuCoins}
              variant="blue"
            />
          </div>

          <div className="eco-card space-y-3">
            <h3 className="text-base font-black text-slate-900">Top Redeemed Rewards</h3>
            {!gamification || gamification.most_redeemed_rewards.length === 0 ? (
              <div className="p-6 text-center text-slate-500 font-bold text-xs bg-slate-50 rounded-2xl border border-slate-200">
                No rewards redeemed yet.
              </div>
            ) : (
              <div className="space-y-2">
                {gamification.most_redeemed_rewards.map((r) => (
                  <div
                    key={r.reward_id}
                    className="p-3 bg-slate-50 rounded-2xl border border-slate-200 flex items-center justify-between text-xs"
                  >
                    <span className="font-extrabold text-slate-900">{r.name}</span>
                    <div className="flex items-center gap-3">
                      <span className="text-slate-600">{formatNumber(r.redemptions_count)} claims</span>
                      <span className="text-sun-800 font-black">{formatNumber(r.total_points_spent)} pts spent</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB CONTENT: Predictions */}
      {activeTab === 'predictions' && (
        <div className="space-y-6 animate-in fade-in">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <StatCard
              title="Total Forecasts"
              value={formatNumber(predictions?.total_predictions ?? 0)}
              subtitle="ML inferences executed"
              icon={Sparkles}
              variant="yellow"
            />
            <StatCard
              title="Avg Forecast Fill"
              value={formatPercentage(predictions?.average_predicted_fill ?? 0)}
              subtitle="Predicted fill rate"
              icon={TrendingUp}
              variant="blue"
            />
            <StatCard
              title="Critical Forecasts"
              value={formatNumber(predictions?.high_fill_predictions_count ?? 0)}
              subtitle="Bins forecast ≥ 80%"
              icon={AlertTriangle}
              variant="coral"
            />
          </div>
        </div>
      )}

      {/* TAB CONTENT: AI Classifications */}
      {activeTab === 'classifications' && (
        <div className="space-y-6 animate-in fade-in">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <StatCard
              title="Total Classifications"
              value={formatNumber(classifications?.total_classifications ?? 0)}
              subtitle="Neural evaluations"
              icon={Bot}
              variant="blue"
            />
            <StatCard
              title="Avg Model Confidence"
              value={formatPercentage(classifications?.average_confidence ? classifications.average_confidence * 100 : 0)}
              subtitle="Classification accuracy"
              icon={LuTarget}
              variant="green"
            />
            <StatCard
              title="Low Confidence Scans"
              value={formatNumber(classifications?.low_confidence_count ?? 0)}
              subtitle="Scans requiring verification"
              icon={AlertTriangle}
              variant="coral"
            />
          </div>

          <div className="eco-card space-y-3">
            <h3 className="text-base font-black text-slate-900">Categories Identified by AI</h3>
            {!classifications || Object.keys(classifications.classifications_by_waste_type).length === 0 ? (
              <div className="p-6 text-center text-slate-500 font-bold text-xs bg-slate-50 rounded-2xl border border-slate-200">
                No AI waste classifications logged yet.
              </div>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {Object.entries(classifications.classifications_by_waste_type).map(([cat, count]) => (
                  <div key={cat} className="p-3.5 bg-slate-50 rounded-2xl border border-slate-200">
                    <p className="text-[10px] uppercase font-bold text-slate-400 truncate">{cat}</p>
                    <p className="text-2xl font-black text-slate-900 mt-1">{formatNumber(count)}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
