import React, { useState, useEffect } from 'react';
import { reportsApi } from '../../api/reports';
import { WasteReport } from '../../types';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { EmptyState } from '../../components/common/EmptyState';
import { LuFilter, LuCalendar, LuFileText } from 'react-icons/lu';

export const StaffReportsPage: React.FC = () => {
  const [reports, setReports] = useState<WasteReport[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchReports = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await reportsApi.getReports({
        status: statusFilter || undefined,
        limit: 50,
      });
      setReports(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch reports.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [statusFilter]);

  return (
    <div className="max-w-5xl mx-auto py-4 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-black uppercase tracking-wider text-blue-700 bg-blue-100 px-3 py-1 rounded-full border border-blue-200">
            Staff Operations
          </span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
            Campus Waste Reports
          </h1>
          <p className="text-slate-600 text-sm font-medium">
            Inspect reported issues across DBIT campus buildings.
          </p>
        </div>

        {/* Status Filter */}
        <div className="flex items-center gap-2">
          <LuFilter className="w-4 h-4 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 rounded-2xl border border-slate-200 text-xs font-bold text-slate-700 bg-white shadow-xs focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <option value="">All Statuses</option>
            <option value="PENDING">Pending</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="RESOLVED">Resolved</option>
            <option value="REJECTED">Rejected</option>
          </select>
        </div>
      </div>

      {loading ? (
        <LoadingState message="Loading campus waste reports..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchReports} />
      ) : reports.length === 0 ? (
        <EmptyState
          icon={LuFileText}
          title="No reports matching filter"
          description="There are currently no reports with this status on campus."
        />
      ) : (
        <div className="space-y-3">
          {reports.map((report) => (
            <div
              key={report.report_id}
              className="eco-card p-5 border-2 border-slate-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:border-blue-200 transition-all"
            >
              <div className="space-y-1.5 flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-black text-slate-900 capitalize">
                    {report.report_type.replace(/_/g, ' ')}
                  </span>
                  <span className="text-[10px] font-bold text-slate-400">
                    Report #{report.report_id}
                  </span>
                </div>
                {report.description && (
                  <p className="text-xs text-slate-600 font-medium">{report.description}</p>
                )}
                <div className="flex items-center gap-3 text-[11px] font-semibold text-slate-400">
                  <span className="flex items-center gap-1">
                    <LuCalendar className="w-3 h-3" />
                    {new Date(report.created_at).toLocaleDateString()}
                  </span>
                  {report.bin && <span>• Bin: {report.bin.bin_code}</span>}
                  {report.user && <span>• By: {report.user.name}</span>}
                </div>
              </div>

              <StatusBadge status={report.status} type="report" />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
