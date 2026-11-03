import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { reportsApi } from '../../api/reports';
import { binsApi } from '../../api/bins';
import { WasteReport, Bin } from '../../types';
import { StatCard } from '../../components/common/StatCard';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { StatusBadge } from '../../components/common/StatusBadge';
import { ProgressBar } from '../../components/common/ProgressBar';
import { LuTriangleAlert, LuTrash2, LuShieldCheck, LuChartBar, LuArrowRight } from 'react-icons/lu';
import { Link } from 'react-router-dom';

export const StaffDashboard: React.FC = () => {
  const { user } = useAuth();
  const [reports, setReports] = useState<WasteReport[]>([]);
  const [bins, setBins] = useState<Bin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStaffData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [reportsRes, binsRes] = await Promise.all([
        reportsApi.getReports({ limit: 10 }).catch(() => []),
        binsApi.getBins({ limit: 50 }).catch(() => []),
      ]);
      setReports(reportsRes);
      setBins(binsRes);
    } catch (err: any) {
      setError(err.message || 'Failed to load staff operational metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStaffData();
  }, []);

  if (loading) {
    return <LoadingState message="Loading staff operational view..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={fetchStaffData} />;
  }

  const openReportsCount = reports.filter((r) => r.status === 'PENDING' || r.status === 'IN_PROGRESS').length;
  const highFillBinsCount = bins.filter((b) => b.current_fill_percentage >= 80).length;
  const activeBinsCount = bins.filter((b) => b.status === 'ACTIVE').length;

  return (
    <div className="max-w-5xl mx-auto py-4 space-y-8">
      {/* Header */}
      <div>
        <span className="text-xs font-black uppercase tracking-wider text-blue-700 bg-blue-100 px-3 py-1 rounded-full border border-blue-200">
          Campus Staff Portal
        </span>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
          Operational Overview
        </h1>
        <p className="text-slate-600 text-sm font-medium">
          Monitor campus bin status, open cleanliness issues, and campus waste activity.
        </p>
      </div>

      {/* Operational Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <StatCard
          title="Open Issue Reports"
          value={openReportsCount}
          subtitle="Awaiting facility review"
          icon={LuTriangleAlert}
          variant="coral"
        />
        <StatCard
          title="High-Fill Bins"
          value={highFillBinsCount}
          subtitle="Bins filled ≥ 80%"
          icon={LuTrash2}
          variant="yellow"
        />
        <StatCard
          title="Active Campus Bins"
          value={activeBinsCount}
          subtitle={`${bins.length} total units deployed`}
          icon={LuShieldCheck}
          variant="green"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Urgent Reports */}
        <div className="eco-card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-extrabold text-slate-900 flex items-center gap-2">
              <LuTriangleAlert className="w-5 h-5 text-coral-600" />
              <span>Recent Campus Reports</span>
            </h3>
            <Link to="/staff/reports" className="text-xs font-bold text-blue-600 hover:text-blue-700">
              View All
            </Link>
          </div>

          {reports.length === 0 ? (
            <p className="text-center py-8 text-xs font-bold text-slate-400">
              No recent reports on campus
            </p>
          ) : (
            <div className="space-y-3">
              {reports.slice(0, 5).map((r) => (
                <div
                  key={r.report_id}
                  className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 flex items-center justify-between"
                >
                  <div>
                    <p className="text-xs font-extrabold text-slate-800 capitalize">
                      {r.report_type.replace(/_/g, ' ')}
                    </p>
                    <p className="text-[11px] font-medium text-slate-500 truncate max-w-[200px]">
                      {r.description || 'No description provided'}
                    </p>
                  </div>
                  <StatusBadge status={r.status} type="report" size="sm" />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* High Fill Bins Requiring Attention */}
        <div className="eco-card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-extrabold text-slate-900 flex items-center gap-2">
              <LuChartBar className="w-5 h-5 text-blue-600" />
              <span>Bins Approaching Capacity</span>
            </h3>
            <Link to="/staff/bins" className="text-xs font-bold text-blue-600 hover:text-blue-700">
              Inspect All
            </Link>
          </div>

          <div className="space-y-3">
            {bins
              .slice()
              .sort((a, b) => b.current_fill_percentage - a.current_fill_percentage)
              .slice(0, 4)
              .map((bin) => (
                <div
                  key={bin.bin_id}
                  className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-xs font-extrabold text-slate-800">{bin.bin_code}</span>
                      <span className="text-[10px] text-slate-400 ml-2">
                        {bin.location?.name || 'Main Campus'}
                      </span>
                    </div>
                    <StatusBadge status={bin.status} type="bin" size="sm" />
                  </div>
                  <ProgressBar
                    value={bin.current_fill_percentage}
                    variant={bin.current_fill_percentage >= 80 ? 'coral' : 'green'}
                    showPercentage={true}
                  />
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
};
