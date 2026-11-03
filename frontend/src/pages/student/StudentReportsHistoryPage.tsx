import React, { useState, useEffect } from 'react';
import { reportsApi } from '../../api/reports';
import { WasteReport } from '../../types';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { EmptyState } from '../../components/common/EmptyState';
import { LuTriangleAlert, LuPlus, LuCalendar, LuCircleCheck, LuFileText } from 'react-icons/lu';
import { Link } from 'react-router-dom';

export const StudentReportsHistoryPage: React.FC = () => {
  const [reports, setReports] = useState<WasteReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchReports = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await reportsApi.getReports({ limit: 50 });
      setReports(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load report history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  if (loading) {
    return <LoadingState message="Loading your submitted reports..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={fetchReports} />;
  }

  return (
    <div className="max-w-4xl mx-auto py-4 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-black uppercase tracking-wider text-coral-700 bg-coral-100 px-3 py-1 rounded-full border border-coral-200">
            My Submissions
          </span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
            Waste Issue Reports
          </h1>
          <p className="text-slate-600 text-sm font-medium">
            Track status updates and point resolutions for your reported campus issues.
          </p>
        </div>

        <Link
          to="/student/report"
          className="btn-3d btn-3d-coral px-5 py-3 text-xs font-black flex items-center justify-center gap-2 shadow-3d-coral shrink-0"
        >
          <LuPlus className="w-4 h-4" />
          <span>Report New Issue</span>
        </Link>
      </div>

      {/* Reports List */}
      {reports.length === 0 ? (
        <EmptyState
          icon={LuFileText}
          title="No reports submitted yet"
          description="If you see an overflowing or damaged bin on campus, let facilities know to earn eco points!"
          actionText="File a Waste Report"
          onAction={() => window.location.assign('/student/report')}
        />
      ) : (
        <div className="space-y-4">
          {reports.map((report) => (
            <div
              key={report.report_id}
              className="eco-card p-5 border-2 border-slate-200/80 hover:border-coral-200 transition-all space-y-3"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-coral-100 text-coral-700 flex items-center justify-center shadow-xs">
                    <LuTriangleAlert className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-extrabold text-slate-900 capitalize">
                      {report.report_type.replace(/_/g, ' ')}
                    </h3>
                    <p className="text-[11px] font-semibold text-slate-400 flex items-center gap-2 mt-0.5">
                      <span className="flex items-center gap-1">
                        <LuCalendar className="w-3 h-3" />
                        {new Date(report.created_at).toLocaleDateString()}
                      </span>
                      <span>•</span>
                      <span>Report #{report.report_id}</span>
                    </p>
                  </div>
                </div>
                <StatusBadge status={report.status} type="report" />
              </div>

              {report.description && (
                <p className="text-xs text-slate-600 font-medium bg-slate-50 p-3 rounded-2xl border border-slate-200/80">
                  {report.description}
                </p>
              )}

              {/* Resolution Notes if Resolved */}
              {report.status === 'RESOLVED' && (
                <div className="p-3 bg-eco-50 rounded-2xl border border-eco-200 text-xs font-bold text-eco-900 flex items-center gap-2">
                  <LuCircleCheck className="w-4 h-4 text-eco-600 shrink-0" />
                  <span>
                    Resolved by Campus Staff
                    {report.resolution_notes ? `: ${report.resolution_notes}` : ' — Points awarded!'}
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
